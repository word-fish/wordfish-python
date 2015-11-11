'''
run_analysis.py

USAGE:

python run_analysis.py /path/to/wordfish/base

This script will merge all terms and corpus into a common framework, and then produce simple
analyses related to term frequency in corpus, etc. Custom analyses scripts can be based off of this. 
For now, the method is as follows:

    - Merge terms and relationships into a common corpus
    - For all text extract features with deep learning (word2vec)
    - For each set of terms, parse over text and find occurrences

     Need to think about how to do this for one at a time... here is where we may need
     to write to database :)

'''

# First train simple word2vec model with different corpus
from wordfish.analysis import train_word2vec_model, save_models, export_models_tsv, load_models
from wordfish.corpus import get_corpus
from wordfish.terms import get_terms
from wordfish.utils import mkdir
import sys

base_dir = sys.argv[1]

# Setup analysis output directory
analysis_dir = mkdir("%s/analysis" %(base_dir))
model_dir = mkdir("%s/models" %(analysis_dir))

corpus = get_corpus(analysis_dir)

# Train corpus specific models
models = dict()
combined_sentences = []
for corpus_id,sentences in corpus.iteritems():
    print "Training model for corpus %s" %(corpus_id)
    models[corpus_id] = train_word2vec_model(sentences)
    combined_sentences = sentences + combined_sentences

# Train model for all corpus
print "Training model for all corpus combined"
models["all"] = train_word2vec_model(combined_sentences)

# Export models to tsv, and save
save_models(models,base_dir)
export_models_tsv(models,base_dir)

# TESTING TESTING TESTING TESTING TESTING

# Get all terms
#models = load_models(analysis_dir)
model = models["neurosynth"]
terms = merge_terms(analysis_dir,subset=True)
intersects = vocab_term_intersect(terms,model)

# For each set of terms, find overlap with neurosynth model
for tag,ints in intersects.iteritems():
    vs = numpy.unique([x[3] for x in ints]).tolist()
    export_models_tsv({"neurosynth_%s" %(tag):model},base_dir,vocabs=[vs])

# Now combine all terms
terms = merge_terms(analysis_dir,subset=False)
intersects = vocab_term_intersect(terms,model)
vs = numpy.unique([x[3] for x in intersects["all"]]).tolist()
export_models_tsv({"neurosynth_all":model},base_dir,vocabs=[vs])

#TODO:
# add method to give plugins ability to define labels (neurosynth)
# This should be a matrix of term_uid (rows) by labels (cols) - binary to start [0,1]
# make method to visualize matrices
# redo installation, re-run scripts to produce all data
# THEN give a go at using labels to do classification
# when have vision for how to do ideal analysis, write up, do it.
