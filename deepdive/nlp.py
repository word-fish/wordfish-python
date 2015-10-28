'''
nlp: part of the deepdive python package
functions for simple natural language processing

'''

from textblob import TextBlob, Word
from nltk.stem.porter import *
from nltk.stem import *
import numpy
import pandas
import re

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
