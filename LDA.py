from gensim import corpora, models
from gensim.matutils import hellinger
from collections import defaultdict
import sys
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def createDict(path, docNum):
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


if(__name__ == '__main__'):
    arg1 = sys.argv[1] if len(sys.argv) > 1 else './data/data.csv'
    arg2 = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    arg3 = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    #encoding features as bijection with some numerical set using dictionary
    myDict = createDict(arg1, arg2)
    #creating two identical corpora. Necessary since corpora is implemented as generator coroutine
    myCorpus = CaseCorpus(arg1, myDict)
    yourCorpus = CaseCorpus(arg1, myDict)

    #transforming corpus using term-frequency inverse-document-frequency
    tfidf = models.TfidfModel(myCorpus)
    #your_tfidf = tfidf[yourCorpus]

    model = models.LdaModel(yourCorpus, id2word = myDict, num_topics = arg3)
    #model.show_topics(num_topics=arg3, num_words = 10, log=False, formatted=True)
    dum_doc = ['finance', 'money', 'sell']
    stupid_doc = ['divorce', 'alimony', 'support']

    dum_bow = model.id2word.doc2bow(dum_doc)
    stupid_bow = model.id2word.doc2bow(stupid_doc)

    dum_lda = model[dum_bow]
    stupid_lda = model[dum_bow]
    print(hellinger(dum_lda, stupid_lda))

