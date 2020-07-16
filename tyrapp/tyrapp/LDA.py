from tyrapp import app
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
doc_num = 1000
num_topics = 50
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

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


data_path = app.config['DATA_PATH']
with open(os.path.join(data_path, 'obj_ids.p'), 'rb') as pickle_file:
    mongo_ids = pickle.load(pickle_file)

def query_hellinger(doc, corpus, model, threshold = 0.3,limit = 100):
    doc_bow = model.id2word.doc2bow(doc)
    doc_lda = model[doc_bow]
    lda_tuples = [(doc_lda, model_lda) for model_lda in model[corpus]]
    corpus_hellinger = pool.starmap(hellinger, lda_tuples)
    zipped_corpus = list(zip(mongo_ids, corpus_hellinger))
    filtered_corpus = list(filter(lambda x: x[1] < threshold, zipped_corpus))
    filtered_corpus.sort(key = lambda x: x[1])
    return [x[0] for x in filtered_corpus]

if(__name__ == '__main__'):
    if(len(sys.argv) > 1):
        data_path = sys.argv[1]
    if(len(sys.argv) > 2):
        doc_num = int(sys.argv[2])
    if(len(sys.argv) > 3):
        num_topics = int(sys.argv[3])
    #encoding features as bijection with some numerical set using dictionary
    myDict = create_dict(data_path, doc_num)
    #creating two identical corpora. Necessary since corpora is implemented as generator coroutine
    myCorpus = CaseCorpus(data_path, myDict)
    yourCorpus = CaseCorpus(data_path, myDict)

    #transforming corpus using term-frequency inverse-document-frequency
    #tfidf = models.TfidfModel(myCorpus)
    #your_tfidf = tfidf[yourCorpus]

    model = models.LdaModel(myCorpus, id2word = myDict, num_topics = num_topics)
    #model.show_topics(num_topics=num_topics, num_words = 10, log=False, formatted=True)
    dum_doc = ['finance', 'money', 'sell']
    #stupid_doc = ['divorce', 'alimony', 'support']
    print(query_hellinger(dum_doc, yourCorpus, model, threshold = 0.7))
    model.save(model_file)