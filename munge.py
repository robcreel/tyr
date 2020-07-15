import os
import shutil
import wget
from xtract import xtract

#only downloads/extracts once for efficiency
if (not os.path.exists('./data')):
        ill_url = "https://api.case.law/v1/bulk/22342/download/"
        os.mkdir('./data')
        os.chdir('./data')
        #download file from caselaw access project api 
        wget.download(ill_url, './')

        #extract data file from weird nested compressed folder structure 
        xtract('./Illinois-20200302-xml.zip', './')
        xtract('./Illinois-20200302-xml/Illinois-20200302-xml/data/data.jsonl.xz', './')

        #move file to reasonable place
        os.rename('./Illinois-20200302-xml/Illinois-20200302-xml/data/data.jsonl', './cases.jsonl')

        #clean up directory structure
        shutil.rmtree('./Illinois-20200302-xml')
        os.remove('./Illinois-20200302-xml.zip')

        #return to project root
        os.chdir('../')


#assuming above is successful or skipped, continue loading the following generic dependencies
import json
import xml.etree.ElementTree as et
import re
import multiprocessing as mp
import sys
import math
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client['tyrdb']
case_col = db['cases']


#nlp module import and model initialization
import nltk

#downloading various modules onto your system 
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.tokenize import word_tokenize

from nltk.corpus import stopwords
sws = stopwords.words('english')

from nltk.stem import WordNetLemmatizer
lm = WordNetLemmatizer()



#defining functions

def mongoAddCase(case, text):
    d = {
        'name': case['name'],
        'date': case['decision_date'],
        'text': text
    }
    return str(case_col.insert_one(d).inserted_id)

def xmlToStrings(xml):
    return et.tostring(et.fromstring(xml['casebody']['data']), encoding='utf-8', method='text').decode()

def scrubPunct(txt):
    doc = re.sub(r'[-\(\)]', ' ', txt)
    return re.sub(r'[^a-zA-Z0-9 ]', '', doc)

def tokenize(doc):
    return word_tokenize(doc)

def lemmatize(wordList):
    return [lm.lemmatize(word.lower()) for word in wordList]

def removeStops(wordList):
    return [word for word in wordList if word not in sws]

def listToLine(wordList):
    line = ','.join(wordList)
    return line + '\n'

#process pool leaves you a cpu core for other things while you're waiting
pool = mp.Pool(os.cpu_count() - 1)

print('Loading File')

arg = int(sys.argv[1]) if len(sys.argv) > 1 else math.inf
with open('./data/cases.jsonl') as file:
    cases = []
    for index, line in enumerate(file):
        if( index >= arg ): break
        else:
            cases.append(json.loads(line))
print('Parsing XML')
caseStrings = pool.map(xmlToStrings, cases)
print('Populating database')
mongoose = []

for i, case in enumerate(cases):
    mongoose.append(mongoAddCase(case,caseStrings[i]))

with open('./data/idhash.txt', 'w') as out:
    out.write('\n'.join(mongoose))
print('Scrubbing punctuation')
scrubbedStrings = pool.map(scrubPunct, caseStrings)
print('Tokenizing')
tokenized = pool.map(tokenize, scrubbedStrings)
print('Lemmatizing')
lemmatized = pool.map(lemmatize, tokenized)
print('Removing Stopwords')
unStopped = pool.map(removeStops, lemmatized)
print('Outputting to CSV')
lines = pool.map(listToLine, unStopped)

with open('./data/data.csv', 'w') as out:
    out.writelines(lines)
print(':-)')


















