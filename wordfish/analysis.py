'''
analysis.py

part of the wordfish python package: extracting relationships of terms from corpus

Copyright (c) 2015-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to 
do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from wordfish.nlp import (
    text2sentences, 
    sentence2words, 
    find_phrases
)
from wordfish.utils import read_json

from gensim.models import Word2Vec, Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from glob import glob
from numpy import average
import numpy
import os
import pandas
import sys

# Training ######################################################################

class TrainSentences(object):
    ''' 
        TrainSentences will produce an iterator of sentences for training. 
        The intended use is for building a word2vec model, as the sentences 
        are revealed as sets of words (or the pieces that are presented 
        in the file
    '''

    def __init__(self, text_files=None,
                       text_list=None, 
                       remove_stop_words=True,
                       remove_non_english_chars=True):

       ''' either text_files (a list of files) or file_list) a list of strings,
           each the text from a doc) must be defined. 
           text_files takes preference over file_list '''

       # The user must provide one of either inputs
       if text_files == None and text_list == None:
           print('''Please define either text_files (a list of file paths) 
                    or file_list (a list of strings)''')
           sys.exit(1)

       self.files = text_files
       self.text_list = text_list
       self.remove_non_english_chars = remove_non_english_chars
       self.remove_stop_words = remove_stop_words

    def __str__(self):
        if self.files != None:
            return '%s files' %len(self.files)
        elif self.text_list != None:
            return '%s texts' %len(self.text_list)
        return "TrainSentence"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):

        if self.files != None:

            # Iterating over a list of file paths
            for input_file in self.files:
                for text in open(input_file, "r").readlines():
                    for line in text2sentences(text, remove_non_english_chars=self.remove_non_english_chars):            
                        words = sentence2words(line, remove_stop_words=self.remove_stop_words)
                        yield words

        else:

            # Iterating over a list of text
            for text in self.text_list:
                for line in text2sentences(text, remove_non_english_chars=self.remove_non_english_chars):            
                    words = sentence2words(line, remove_stop_words=self.remove_stop_words)
                    yield words


class LabeledLineSentence(object):
    '''LabeledLineSentence does equivalent preprocessing of documents, but then yields a labeled 
    sentence. The intention is for use with doc2vec'''
    def __init__(self,
                labels_list,
                text_files=None,
                remove_stop_words=True, 
                remove_non_english_chars=True):

       self.labels_list = labels_list
       self.text_files = text_files
       self.remove_stop_words = remove_stop_words
       self.remove_non_english_chars = remove_non_english_chars

    def __str__(self):
        if self.files != None:
            return '%s files' %len(self.text_files)
        return "LabeledLineSentence"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        labels = self.labels_list.copy()
        for text_file in self.text_files:
            label = labels.pop(0)
            words_list = TrainSentences(text_files=[text_file],
                                        remove_stop_words=self.remove_stop_words,
                                        remove_non_english_chars=self.remove_non_english_chars)
            for text in words_list:
                yield TaggedDocument(words=text, tags=[label])


def train_word2vec_model(text_files=None,
                         text_list=None, 
                         remove_non_english_chars=True,
                         remove_stop_words=True,
                         min_count=1,
                         workers=8,
                         size=300):

    '''train_word2vec_model is a wrapper for TrainSentences, endsuring that we use
       gensim's word2vec with TrainingSentences derived from some corpus'''

    sentences = TrainSentences(text_files=text_files,
                               text_list=text_list,
                               remove_stop_words=remove_stop_words,
                               remove_non_english_chars=remove_non_english_chars)
    return Word2Vec(sentences, size=size, workers=workers, min_count=min_count)


def train_doc2vec_model(text_labels,
                        text_files=None,
                        iters=10,
                        remove_non_english_chars=True,
                        remove_stop_words=True,
                        size=300, min_count=1, workers=8, 
                        alpha=0.025, min_alpha=0.025):
    '''train_doc2vec_model will let us input a file with a corresponding label
       (intended to be associated with a document). It is a wrapped for 
       LabeledLineSentence.'''

    lls = LabeledLineSentence(text_files=text_files,
                              labels_list=text_labels,
                              remove_stop_words=remove_stop_words,
                              remove_non_english_chars=remove_non_english_chars)

    model = Doc2Vec(lls,
                    vector_size=size, 
                    window=10,
                    min_count=min_count,
                    workers=workers,
                    alpha=alpha, 
                    min_alpha=min_alpha) # use fixed learning rate

    for it in range(iters):
        print("Training iteration %s" %(it))
        model.train(docs)
        model.alpha -= 0.002 # decrease the learning rate
        model.min_alpha = model.alpha # fix the learning rate, no decay
        model.train(labeledDocs)
    return model

# Classification ###############################################################

class DeepTextAnalyzer(object):

    def __init__(self, word2vec_model):
        # https://dato.com/learn/gallery/notebooks/deep_text_learning.html
        """
        Construct a DeepTextAnalyzer using the input Word2Vec model
        :param word2vec_model: a trained Word2Vec model
        """
        self.model = word2vec_model

    def text2vectors(self,text):
        """
        Convert input text into an iterator that returns the corresponding vector representation of each
        word in the text, if it exists in the Word2Vec model
        :param txt: input text
        :param is_html: if True, then extract the text from the input HTML
        :return: iterator of vectors created from the words in the text using the Word2Vec model.
        """
        words = sentence2words(text)
        words = [w for w in words if w in self.model]
        if len(words) != 0:
            for w in words:
                yield self.model[w]

    def text2mean_vector(self,text,read_file=True):
        """
        Calculate the average vector representation of the input text
        :param txt: input text
        :param is_html: is the text is a HTML
        :return the average vector of the vector representations of the words in the text  
        """
        if read_file == True:
            text = open(text,"rb").read().strip("\n")
        vectors = self.text2vectors(text)
        vectors_sum = next(vectors, None)
        if vectors_sum is None:
            return None
        count = 1.0
        for v in vectors:
            count += 1
            vectors_sum = numpy.add(vectors_sum,v)
        # calculate the average vector and replace +infy and -inf with numeric values 
        avg_vector = numpy.nan_to_num(vectors_sum/count)
        return avg_vector


def save_models(models, output_dir, ext='word2vec'):
    '''
    save_models: should be a dictionary with tags as keys, models as value
    '''
    for model_key,model in models.items():
        model.save("%s/%s.%s" %(output_dir, model_key, ext))


def load_models(base_dir,model_keys=None):
    if isinstance(model_keys,str): model_keys = [model_keys]
    models = dict()
    model_dir = "%s/analysis/models" %(base_dir)
    if model_keys == None:
        model_keys = glob("%s/*.word2vec" %(model_dir))
        model_keys = [os.path.basename(x).replace(".word2vec","") for x in model_keys]
    for model_key in model_keys:
        model_file = "%s/%s.word2vec" %(model_dir,model_key)
        if os.path.exists(model_file):
            models[model_key] = Word2Vec.load(model_file)
    return models

def export_vectors(models, output_dir, sep="\t"):
    for model_name,model in models.items():
        print("Processing %s" %(model_name))
        vectors = extract_vectors(model)
        output_tsv = "%s/%s.tsv" %(output_dir, model_name)
        vectors.to_csv(output_tsv,sep=sep)


def extract_vectors(model, vocab=None):
    if vocab == None:
        vocab = model.wv.vocab
    vectors = pandas.DataFrame(columns=range(model.vector_size))
    for v in vocab:
        vectors.loc[v] = model.wv[v]
    return vectors

# This is very slow - likely we can extract matrix from model itself
def extract_similarity_matrix(model, vocab=None):
    if vocab==None:
        vocab = model.wv.vocab
    simmat = pandas.DataFrame(columns=vocab)
    terms = list(vocab.keys())
    for term, v in vocab.items():
        print("parsing %s" %(term))
        sims = model.most_similar(term,topn=len(terms))
        values = [sims[x][1] for x in range(len(sims)) if sims[x][0] in vocab]
        labels = [sims[x][0] for x in range(len(sims)) if sims[x][0] in vocab]
        simmat.loc[term, labels] = values
    return simmat

def vocab_term_intersect(terms, model):
    '''
    Finds the intersection of a terms data structure and model.
    Uses a stemming method to stem both, and find overlap.
    Returns a dictionary, with 

       [key]--> model name
       [value]--> tuples in form
       (term_index,vocab_index,term,vocab)

    repeat: the number of times to go over the text (appropriate for
    longer text with possible repetition of terms)
    '''
    vocab = model.vocab.keys()
    intersects = dict()
    for tag,term_set in terms.items():
        if isinstance(term_set,dict):
            names = [x["name"] for x in term_set["nodes"].values()] 
            phrases = find_phrases(words=names,vocabulary=vocab)
            # Returns (word index,vocab index, word, vocab)
            # (697, 3160, u'somatosensation', 'somatosensory')
            intersects[tag] = phrases
    return intersects


def get_labels(meta):
    labels = []
    for r in range(len(meta)):
        meta_file = meta[r]
        labels = numpy.unique(labels + read_json(meta_file)["labels"]).tolist() 
    return labels


def featurize_to_corpus(model, meta, fillna=True):
    '''featurize_to_corpus

    ## STOPPED HERE. Need to update this to not install on server, etc.
    generate average feature vectors for a set of documents and their labels based
    on an existing model (model). The meta json file should describe text and labels
    '''   
    analyzer = DeepTextAnalyzer(model)
    vectors = pandas.DataFrame(columns=range(model.vector_size))
    # Get all unique term names from the meta objects
    term_names = get_labels(meta=meta)
    # Create a matrix of labels, keep track of which abstracts are labeled
    labels = pandas.DataFrame(columns=term_names)
    for r in range(len(meta)):
        meta_file = meta[r]
        text = meta_file.replace("_meta","_sentences")
        label = os.path.basename(text).split("_")[0]
    # Build a model for everyone else
    if label not in vectors.index:
        try:
            print("Processing %s of %s" %(r,len(meta)))
            vectors.loc[label] = analyzer.text2mean_vector(text)
            labels.loc[label,read_json(meta_file)["labels"]] = 1
        except:
            pass
    count = 1
    for r in range(len(meta)):
        meta_file = meta[r]
        post = meta_file.replace("_meta","_sentences")
        # Build a model by taking the mean vector
        if count not in vectors.index:
            try:
                print("Processing %s of %s" %(r,len(meta)))
                vectors.loc[count] = analyzer.text2mean_vector(post)
                labels.loc[count,read_json(meta_file)["labels"]] = 1
                count+=1
            except:
                pass
    if fillna:
        labels = labels.fillna(0)
        vectors = vectors.fillna(0)
    return vectors,labels
