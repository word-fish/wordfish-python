'''
corpus.py

part of the wordfish python package: extracting relationships of terms from corpus
this set of functions works with different plugins (in plugins folder) to produce input corpus
for parsing.

'''

from wordfish.utils import find_directories, save_pretty_json
from wordfish.nlp import remove_nonenglish_chars
from textblob import TextBlob
from glob import glob
import os

            
def save_sentences(articles,output_dir=".",prefix=""):
    '''save_sentences: 
    parses a dictionary with articles and sentences into output sentence files
    Parameters
    ==========
    articles: list or dict
        a list or dictionary of articles to parse and save to sentences.txt files.
        If you have a meaningful unique ID, provide a dictionary with the UID as key
        If not, provide a list and an integer will be generated instead.
    output_dir: path
        full path that corresponds to the plugins specific directory under "corpus"
        eg $WORK/corpus/neurosynth
    '''
    if isinstance(articles,dict):
        for uid, meta in articles.iteritems():
            meta["text"] = remove_nonenglish_chars(meta["text"])
            save_sentences_single(uid,meta["text"],output_dir,prefix)
            # If more than one entry is provided, we also have meta data
            if len(meta)>1:
                save_meta(uid,meta,output_dir)

    elif isinstance(articles,list):
        for uid in range(len(articles)):
            articles["uid"] = remove_nonenglish_chars(articles["uid"])
            save_sentences_single(uid,articles[uid],output_dir,prefix)

def save_sentences_single(uid,text,output_dir,remove_non_english_chars=True,prefix=""):
    '''save_sentence_single
    Write text to file 
    Parameters
    ==========
    uid: int or string
        a unique ID for the article
    text: str
        raw text of the article    
    output_dir: path
        full path to a plugins corpus directory
    '''
    if prefix != "":
        prefix = "%s_" %(prefix)
    output_file = "%s/%s%s_sentences.txt" %(output_dir,uid,prefix)
    filey = open(output_file,"wb")
    filey.write("%s\n" %(text))
    filey.close()


def save_meta(uid,meta,output_dir,prefix=""):
    '''save_meta
 
    Parameters
    ==========
    uid: int or string
        a unique ID for the article
    meta: dict
        dictionary with meta info, and labels
    output_dir: path
        full path to a plugins corpus directory
    '''
    if prefix != "":
        prefix = "%s_" %(prefix)
    output_file = "%s/%s_%smeta.txt" %(output_dir,uid,prefix)
    tmp = save_pretty_json(meta,output_file)
    return tmp

def get_meta(base_dir):
    corpus_folders = find_directories("%s/corpus" %(base_dir))
    corpus = dict()
    for folder in corpus_folders:
        corpus_name = os.path.basename(folder)
        meta = glob("%s/*meta*" %(folder))
        if len(meta)>0:
            corpus[corpus_name] = meta
    return corpus


def get_corpus(analysis_dir):
    corpus_folders = find_directories("%s/corpus" %(analysis_dir))
    corpus = dict()
    for folder in corpus_folders:
        corpus_name = os.path.basename(folder)
        sentences = glob("%s/*sentences*" %(folder))
        if len(sentences)>0:
            corpus[corpus_name] = sentences
    return corpus


def subset_corpus(corpus,delim="_",position=0):
    '''subset_corpus
    return a subset of the corpus based on 
    splitting the file name by delimiter "delim" 
    [default is "_"] at position "position" [default is 0]
    '''
    subset = dict()
    for document in corpus:
        topic = os.path.basename(document).split(delim)[position]
        if topic in subset:
            subset[topic].append(document)
        else:
            subset[topic] = [document]
    return subset



