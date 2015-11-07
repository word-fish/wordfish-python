'''
nlp:part of the wordfish python package: extracting relationships of terms from corpus

functions for simple natural language processing

'''

from textblob import TextBlob, Word
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import *
import nltk.data
import numpy
import pandas
import gensim
import re

class TrainSentences(object):
    def __init__(self, text_files):
       self.files = text_files
    def __iter__(self):
        for input_file in self.files:
            for text in file(input_file, "rb"):
                for line in text2sentences(text):            
                    words = sentence2words(line)
                    if len(words) < 3: continue    
                    yield words

def train_word2vec_model(text_files):
    sentences = TrainSentences(text_files)
    model = gensim.models.Word2Vec(sentences, size=300, workers=8, min_count=40)
    return model

def text2sentences(text,remove_non_english_chars=True):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')    
    if remove_non_english_chars:
        text = re.sub("[^a-zA-Z]", " ", text)
    for s in tokenizer.tokenize(text):
        yield s

def sentence2words(sentence,remove_stop_words=True,lower=True):
    if isinstance(sentence,list): sentence = sentence[0]
    re_white_space = re.compile("\s+")
    stop_words = set(stopwords.words("english"))
    if lower: sentence = sentence.lower()
    words = re_white_space.split(sentence.strip())
    if remove_stop_words:
        words = [w for w in words if w not in stop_words]
    return words

def do_stem(words,return_unique=True):
    '''do_stem
    Parameters
    ==========    
    words: str/list
        one or more words to be stemmed
    return_unique: boolean (default True)
        return unique terms
    '''
    stemmer = PorterStemmer()
    if isinstance(words,str):
        words = [words]
    stems = []
    for word in words:
        stems.append(stemmer.stem(word))
    if return_unique:
        return numpy.unique([s.lower() for s in stems]).tolist()
    else:
        return stems

def get_total_words(text):
    '''get_total_words:
    get total words in a text (dict, string, or list)
    Parameters
    ==========
    text: str,dict,list
        some text content to parse to count total words
    Returns
    =======
    totalwords: int
        total count of words
    '''
    totalwords = 0

    # Dictionary
    if isinstance(text,dict):
        for label,sentences in text.iteritems():
            if isinstance(sentences,str):
                sentences = [sentences]
            for sentence in sentences:
                blob =  TextBlob(sentence)
                words = do_stem(blob.words)
                totalwords += len(words)
        return totalwords    

    # String or list
    elif isinstance(text,str):
        text = [text]
    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        totalwords += len(words)
    return totalwords


def get_term_counts(terms,text):
    '''get_term_counts:
    a wrapper for get_term_counts_dict and get_term_counts_list
    will return a pandas data frame of counts for a list of terms of interst
    Parameters
    ==========
    text: dict,list,str
        some text content to parse to count a number of terms
    terms: str,list
        one or more terms to be stemmed and counted in the text
    Returns
    =======
    totalwords: int
        total count of words
    '''
    if isinstance(text,dict):
        return get_term_counts_dict(terms,text)
    elif isinstance(text,str):
        text = [text]
    elif isinstance(text,list):
        return get_term_counts_list(terms,text)


def get_term_counts_list(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=stems)

    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        words = [w for w in words if w in stems]
        counts.loc[words] = counts.loc[words] + 1
    return counts        
    

def get_term_counts_dict(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=stems)

    for label,sentences in text.iteritems():
        if isinstance(sentences,str):
            sentences = [sentences]
        for sentence in sentences:
            blob =  TextBlob(sentence)
            words = do_stem(blob.words)
            words = [w for w in words if w in stems]
            counts.loc[words] = counts.loc[words] + 1
    return counts
