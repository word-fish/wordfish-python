'''
analysis.py

part of the wordfish python package: extracting relationships of terms from corpus

'''

from wordfish.nlp import text2sentences, sentence2words, find_phrases
from glob import glob
import gensim
import pandas

# Training ######################################################################
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

def save_models(models,base_dir):
    '''
    save_models: should be a dictionary with tags as keys, models as value
    '''
    for model_key,model in models.iteritems():
        model.save("%s/analysis/models/%s.word2vec" %(base_dir,model_key))

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
