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
    equation2tokens,
    find_phrases
)
from wordfish.utils import ( read_json, read_file )

from gensim.models import Word2Vec, Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from glob import glob
from numpy import average
import numpy
import os
import pandas
import sys

# Training ######################################################################

class TrainBase(object):
    ''' 
        TrainBase will produce an iterator of sentences for training. 
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
        return "TrainBase"

    def __repr__(self):
        return self.__str__()


# Train Sentences ##############################################################

class TrainSentences(TrainBase):
    ''' 
        TrainSentences will produce an iterator of sentences for training. 
        The intended use is for building a word2vec model, as the sentences 
        are revealed as sets of words (or the pieces that are presented 
        in the file

        Example::

        sentences = TrainSentences(text_files=text_files,
                                   text_list=text_list,
                                   remove_stop_words=remove_stop_words,
                                   remove_non_english_chars=remove_non_english_chars)
        model = Word2Vec(sentences, size=300, workers=8, min_count=1)

    '''
    def __init__(self, text_files=None,
                       text_list=None, 
                       remove_stop_words=True,
                       remove_non_english_chars=True):
        self.name = "TrainSentences"
        super(TrainSentences, self).__init__(text_files, text_list,
                                             remove_stop_words,
                                             remove_non_english_chars)

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


class TrainEquations(TrainBase):
    ''' 
        TrainEquations, meaning we yield tokens that are known latex and 
        character symbols. This will produce an iterator of "equation sentences"
        for training. 
    '''
    def __init__(self, text_files=None,
                       text_list=None, 
                       remove_stop_words=True,
                       remove_non_english_chars=True):

        self.name = "TrainEquations"
        super(TrainEquations, self).__init__(text_files, text_list,
                                             remove_stop_words,
                                             remove_non_english_chars)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):

        if self.files != None:

            # Iterating over a list of file paths
            for input_file in self.files:
                for text in open(input_file, "r").readlines():
                    for line in text2sentences(text, self.remove_non_english_chars):            
                        yield equation2tokens(line) 
        else:
            # Iterating over a list of text
            for text in self.text_list:
                for line in text2sentences(text, remove_non_english_chars=self.remove_non_english_chars):            
                    yield equation2tokens(line) 


class TrainCharacters(TrainBase):
    ''' 
        Do Word2Vec, but use single characters instead of equations tokens. 
    '''
    def __init__(self, text_files=None,
                       text_list=None, 
                       remove_stop_words=True,
                       remove_non_english_chars=True):

        self.name = "TrainCharacters"
        super(TrainCharacters, self).__init__(text_files, text_list,
                                              remove_stop_words,
                                              remove_non_english_chars)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):

        if self.files != None:

            # Iterating over a list of file paths
            for input_file in self.files:
                for text in open(input_file, "r").readlines():
                    for line in text2sentences(text, self.remove_non_english_chars):            
                        for c in line:
                            yield c 
        else:
            # Iterating over a list of text
            for text in self.text_list:
                for line in text2sentences(text, remove_non_english_chars=self.remove_non_english_chars):            
                    for c in line:
                        yield c 


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


# Classification ###############################################################

class DeepAnalyzerBase(object):

    def __init__(self, word2vec_model):
        # https://dato.com/learn/gallery/notebooks/deep_text_learning.html
        '''Construct a DeepTextAnalyzer using the input Word2Vec model

        Parameters
        ==========
        word2vec_model: a trained Word2Vec model
        '''
        self.model = word2vec_model

    def text2vectors(self):
        print("Please instantiate this class, this is an abstract base!")
        sys.exit(1)

    def text2mean_vector(self, text):
        '''Calculate the average vector representation of the input text
           For the sentences analyzer, this means sentences -> words. For
           the equation analyzer, this means equations -> symbols
        
           Parameters
           ==========
           txt: input text
        '''
        vectors = self.text2vectors(text)
        vectors_sum = next(vectors, None)
        if vectors_sum is None:
            return None
        count = 1.0
        for v in vectors:
            count += 1
            vectors_sum = numpy.add(vectors_sum, v)

        # calculate the average vector, replace +infy and -inf w/ numeric values 
        return numpy.nan_to_num(vectors_sum/count)
        

class DeepEquationAnalyzer(DeepAnalyzerBase):

    def __init__(self, model):
        super(DeepEquationAnalyzer, self).__init__(model)

    def text2vectors(self, text):
        '''Convert input string equation into an iterator that returns the 
        corresponding vector representation of each word in the text, if it exists in the 
        Word2Vec model

        Parameters
        ==========
        txt: input text
        returns iterator of vectors, from txt using the Word2Vec model.
        '''
        tokens = equation2tokens(text)
        tokens = [t for t in tokens if self.model.wv.__contains__(t)]
        if len(tokens) > 0:
            for t in tokens:
                yield self.model.wv.__getitem__(t)


class DeepCharacterAnalyzer(DeepAnalyzerBase):

    def __init__(self, model):
        super(DeepCharacterAnalyzer, self).__init__(model)

    def text2vectors(self, text):
        '''Convert input string equation into an iterator that returns the 
        corresponding vector representation of each word in the text, 
        if it exists in the  Word2Vec model

        Parameters
        ==========
        txt: input text
        returns iterator of vectors, from txt using the Word2Vec model.
        '''
        chars = [c for c in text if self.model.wv.__contains__(c)]
        if len(chars) > 0:
            for c in chars:
                yield self.model.wv.__getitem__(c)


class DeepTextAnalyzer(DeepAnalyzerBase):

    def __init__(self, model):
        super(DeepTextAnalyzer, self).__init__(model)

    def text2vectors(self, text):
        '''Convert input text into an iterator that returns the corresponding 
        vector representation of each word in the text, if it exists in the 
        Word2Vec model

        Parameters
        ==========
        txt: input text
        returns iterator of vectors, from txt using the Word2Vec model.
        '''
        words = sentence2words(text)
        words = [w for w in words if w in self.model]
        if len(words) != 0:
            for w in words:
                yield self.model.wv.__getitem__(w)


def save_models(models, output_dir, ext='word2vec'):
    '''
    save_models: should be a dictionary with tags as keys, models as value
    '''
    for model_key,model in models.items():
        model.save("%s/%s.%s" %(output_dir, model_key, ext))


def load_model(model_file):
    if os.path.exists(model_file):
        return Word2Vec.load(model_file)
    
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
