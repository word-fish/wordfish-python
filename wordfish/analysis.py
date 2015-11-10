'''
analysis.py

part of the wordfish python package: extracting relationships of terms from corpus

'''

from wordfish.nlp import text2sentences, sentence2words

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

