'''
analysis.py

part of the wordfish python package: extracting relationships of terms from corpus

'''

from wordfish.nlp import text2sentences, sentence2words, find_phrases
from wordfish.utils import read_json
from numpy import average
from glob import glob
import numpy
import gensim
import pandas
import os

# Training ######################################################################
class TrainSentences(object):
    def __init__(self, text_files,remove_stop_words=True,remove_non_english_chars=True):
       self.files = text_files
    def __iter__(self):
        for input_file in self.files:
            for text in file(input_file, "rb"):
                for line in text2sentences(text,remove_non_english_chars=remove_non_english_chars):            
                    words = sentence2words(line,remove_stop_words=remove_stop_words)
                    if len(words) < 3: continue    
                    yield words

def train_word2vec_model(text_files,remove_non_english_chars=True,remove_stop_words=True):
    sentences = TrainSentences(text_files,remove_stop_words,remove_non_english_chars)
    model = gensim.models.Word2Vec(sentences, size=300, workers=8, min_count=40)
    return model

def train_lda_model(text_files,remove_non_english_chars=True,remove_stop_words=True):
    sentences = TrainSentences(text_files,remove_stop_words,remove_non_english_chars)
    model = gensim.models.Word2Vec(sentences, size=300, workers=8, min_count=40)
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


def save_models(models,base_dir):
    '''
    save_models: should be a dictionary with tags as keys, models as value
    '''
    for model_key,model in models.iteritems():
        model.save("%s/analysis/models/%s.word2vec" %(base_dir,model_key))


def build_models(corpus,model_type="word2vec",remove_non_english_chars=True,remove_stop_words=True):
    models = dict()
    print "Training models..."
    for corpus_id,sentences in corpus.iteritems():
        try:
            if model_type == "word2vec":
                models[corpus_id] = train_word2vec_model(sentences,remove_non_english_chars,remove_stop_words)
            else:
                models[corpus_id] = train_lda_model(sentences,remove_non_english_chars,remove_stop_words)
        except:
            print "Error building model for %s" %(corpus_id)
            pass
    return models


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
            models[model_key] = gensim.models.Word2Vec.load(model_file)
    return models

def export_vectors(models,output_dir,sep="\t"):
    # Export vectors
    for model_name,model in models.iteritems():
        print "Processing %s" %(model_name)
        vecs = extract_vectors(model)
        vecs.to_csv("%s/%s.tsv" %(output_dir,model_name),sep=sep)


def extract_vectors(model,vocab=None):
    if vocab==None:
        vocab = model.vocab.keys()
    length = len(model.__getitem__(vocab[0]))
    vectors = pandas.DataFrame(columns=range(length))
    for v in vocab:
        vectors.loc[v] = model.__getitem__(v)
    return vectors

# This is very slow - likely we can extract matrix from model itself
def extract_similarity_matrix(model,vocab=None):
    if vocab==None:
        vocab = model.vocab.keys()
    nvocab = len(model.vocab.keys())
    simmat = pandas.DataFrame(columns=vocab)
    for v in range(len(vocab)):
        term = vocab[v]
        print "parsing %s of %s: %s" %(v,len(vocab),term)
        sims = model.most_similar(term,topn=nvocab)
        values = [sims[x][1] for x in range(len(sims)) if sims[x][0] in vocab]
        labels = [sims[x][0] for x in range(len(sims)) if sims[x][0] in vocab]
        simmat.loc[v+1,labels] = values
    return simmat

def export_models_tsv(models,base_dir,vocabs=None):
    '''
    export_models_tsv: 
    models: dict
        should be a dictionary with tags as keys, models as value
    vocabs: list
        the vocabulary to extract from each model, must be
        same length as model
    '''
    if vocabs != None:
        if len(vocabs)!=len(models):
            print "There must be a vocab specified for each model."
            return
    count=0
    for tag,model in models.iteritems():
        if vocabs==None:
            export_model_tsv(model,tag,base_dir,vocabs)
        else:
            export_model_tsv(model,tag,base_dir,vocabs[count])
            count+=1
            

def export_model_tsv(model,tag,base_dir,vocab=None):
    '''
    export_model_tsv: 
    model: gensim.Word2Vec object
    tag: tag corresponding to model name (corpus)
    '''
    df = extract_similarity_matrix(model,vocab=vocab)
    df.to_csv("%s/analysis/models/%s.tsv" %(base_dir,tag),sep="\t")
    return df


def vocab_term_intersect(terms,model):
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
    for tag,term_set in terms.iteritems():
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


def featurize_to_corpus(model,meta,size=300,fillna=True):
    '''featurize_to_corpus
    generate average feature vectors for a set of documents and their labels based
    on an existing model (model). The meta json file should describe text and labels
    '''   
    analyzer = DeepTextAnalyzer(model)
    vectors = pandas.DataFrame(columns=range(size))
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
            print "Processing %s of %s" %(r,len(meta))
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
                print "Processing %s of %s" %(r,len(meta))
                vectors.loc[count] = analyzer.text2mean_vector(post)
                labels.loc[count,read_json(meta_file)["labels"]] = 1
                count+=1
            except:
                pass
    if fillna:
        labels = labels.fillna(0)
        vectors = vectors.fillna(0)
    return vectors,labels
