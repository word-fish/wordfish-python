'''
corpus.py

part of the wordfish python package: extracting relationships of terms from corpus
this set of functions works with different plugins (in plugins folder) to produce input corpus
for parsing.

'''

from wordfish.utils import find_directories, save_pretty_json
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
            save_sentences_single(uid,meta["text"],output_dir,prefix)
            # If more than one entry is provided, we also have meta data
            if len(meta)>1:
                save_meta(uid,meta,output_dir)

    elif isinstance(articles,list):
        for uid in range(len(articles)):
            save_sentences_single(uid,articles[uid],output_dir,prefix)

def save_sentences_single(uid,text,output_dir,remove_non_english_chars=True,prefix=""):
    '''save_sentence_single
    Write sentences to file

    88390|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    88391|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    We should use utf-8 http://www.postgresql.org/docs/9.0/static/multibyte.html
 
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
    output_file = "%s/%ssentences.txt" %(output_dir,prefix)
    filey = open(output_file,"ab")
    filey.write('%s|"<text>' %uid)
    blob = TextBlob(text)
    for sentence in blob.sentences:
        sentence = '<p>%s</p>' %sentence.raw.replace("\t","").replace("|"," ").replace("\n","").replace("\r","")
        filey.write(sentence.replace("}","").replace("{","").encode("utf-8"))
    filey.write('</text>"\n')
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


def get_corpus(analysis_dir):
    corpus_folders = find_directories("%s/corpus" %(analysis_dir))
    corpus = dict()
    for folder in corpus_folders:
        corpus_name = os.path.basename(folder)
        sentences = glob("%s/*sentences*" %(folder))
        if len(sentences)>0:
            corpus[corpus_name] = sentences
    return corpus

