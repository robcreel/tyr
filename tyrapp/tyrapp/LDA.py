from gensim import corpora, models
from gensim.matutils import hellinger
from gensim.test.utils import datapath
from collections import defaultdict
import sys
import os
import logging
from multiprocessing import Pool
import pickle



model_file = datapath("model")
pool = Pool(os.cpu_count() - 1)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#training parameters
chunksize =2000
doc_num = 1000
num_topics = 50
iterations = 400
passes = 20
workers = os.cpu_count()-1
eval_every = None

def create_dict(path, docNum):
    dictionaryDocs = []
    freq = defaultdict(int)
    with open(path, 'r') as file:
        for i in range(docNum):
            dictionaryDocs.append(file.readline().split(','))
    for doc in dictionaryDocs:
        for token in doc:
            freq[token] += 1
    texts = [
        [token for token in text if freq[token] > 1]
        for text in dictionaryDocs
    ]
    dictionary = corpora.Dictionary(texts)
    return dictionary

class CaseCorpus(object):
    def __init__(self, path, dictionary):
        self.path = path
        self.dict = dictionary
    def __iter__(self):
        with open(self.path, 'r') as file:
            for line in file:
                yield self.dict.doc2bow(line.split(','))

print('__name__ from LDA', __name__)
if(__name__ == 'tyrapp.LDA'):
    from tyrapp import app
    data_path = app.config['DATA_PATH']
else:
    data_path ='./data'
with open(os.path.join(data_path, 'obj_ids.p'), 'rb') as pickle_file:
    mongo_ids = pickle.load(pickle_file)

def query_hellinger(doc, lda_corpus, model, threshold = 0.3,limit = 100):
    doc_bow = model.id2word.doc2bow(doc)
    doc_lda = model[doc_bow]
    print("Zipping lda vector tuples for starmap")
    lda_tuples = [(doc_lda, other_lda) for other_lda in lda_corpus]
    print("Calculating topical relevence between upload and corpus docs")
    corpus_hellinger = pool.starmap(hellinger, lda_tuples)
    zipped_corpus = list(zip(mongo_ids, corpus_hellinger))
    print("Filtering by topical relevance")
    filtered_corpus = list(filter(lambda x: x[1] < threshold, zipped_corpus))
    print('Sorting by topical relevence')
    filtered_corpus.sort(key = lambda x: x[1])
    print(f"Limiting corpus to {limit} most related documents")
    return [x[0] for x in filtered_corpus]

if(__name__ == '__main__'):
    if(len(sys.argv) > 1):
        doc_num = int(sys.argv[1])
    if(len(sys.argv) > 2):
        num_topics = int(sys.argv[2])
    #encoding features as bijection with some numerical set using dictionary
    csv_path = os.path.join(data_path, 'data.csv')
    myDict = create_dict(csv_path, doc_num)
    #creating two identical corpora. Necessary since corpora is implemented as generator coroutine
    myCorpus = CaseCorpus(csv_path, myDict)

    model = models.LdaMulticore(myCorpus, id2word = myDict, num_topics = num_topics,
                            chunksize=chunksize, iterations = iterations, eval_every=eval_every, workers=workers)
    model.save(model_file)
