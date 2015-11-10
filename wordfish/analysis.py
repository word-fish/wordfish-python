'''
analysis.py

part of the wordfish python package: extracting relationships of terms from corpus

'''

from wordfish.nlp import text2sentences, sentence2words
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
        model.save("%s/analysis/models/%s.word2vec" %(model_dir,model_key))

def load_models(model_keys,model_dir):
    if isinstance(model_keys,str): model_keys = [model_keys]
    models = dict()
    for model_key in model_keys:
        model_file = "%s/%s.word2vec" %(model_dir,model_key)
        if os.path.exists(model_file):
            models[model_key] = gensim.models.Word2Vec.load(model_file)
    return models

# This is very slow - likely we can extract matrix from model itself
def extract_similarity_matrix(model):
    vocab = model.vocab.keys()
    nvocab = len(vocab)
    simmat = pandas.DataFrame(columns=vocab)
    for v in range(2818,nvocab):
        term = vocab[v]
        print "parsing %s of %s: %s" %(v,nvocab,term)
        sims = model.most_similar(term,topn=nvocab)
        values = [x[1] for x in sims]
        labels = [x[0] for x in sims]
        simmat.loc[v+1,labels] = values
    return simmat

def export_models_tsv(models,base_dir):
    '''
    export_models_tsv: 
    models: dict
        should be a dictionary with tags as keys, models as value
    '''
    for tag,model in models.iteritems():
        export_model_tsv(model,tag,analysis_dir)

def export_model_tsv(model,tag,base_dir):
    '''
    export_model_tsv: 
    model: gensim.Word2Vec object
    tag: tag corresponding to model name (corpus)
    '''
    df = extract_similarity_matrix(model)
    df.to_csv("%s/analysis/models/%s.tsv",sep="\t" %(analysis_dir,tag))
    return df

