'''
run_analysis.py

USAGE:

python run_analysis.py

Your wordfish project home directory should be defined as WORDFISH_HOME

This script will merge all terms and corpus into a common framework, and then produce simple
analyses related to term frequency in corpus, etc. Custom analyses scripts can be based off of this. 
For now, the method is as follows:

    - Merge terms and relationships into a common corpus
    - For all text extract features with deep learning (word2vec)
    - For each set of terms, parse over text and find occurrences

     Need to think about how to do this for one at a time... here is where we may need
     to write to database :)

     IMPORTANT: For now, this is all testing. I don't want to implement any definite functions
     until I have a sense of the functionality that I want.

'''

# First train simple word2vec model with different corpus
from wordfish.analysis import train_word2vec_model, save_models, export_models_tsv, load_models, vocab_term_intersect, extract_similarity_matrix, extract_vectors
from wordfish.corpus import get_corpus, get_meta
from wordfish.terms import merge_terms
from wordfish.utils import mkdir
import pandas
import sys
import os

base_dir = os.environ["WORDFISH_HOME"]

# Setup analysis output directory
analysis_dir = mkdir("%s/analysis" %(base_dir))
model_dir = mkdir("%s/models" %(analysis_dir))
vector_dir = mkdir("%s/vectors" %(analysis_dir))

corpus = get_corpus(base_dir)

# Break up reddit corpus by disorder
import wordfish.plugins.reddit.functions as reddit
reddit_corpus = reddit.get_corpus(subset=True)


reddit = corpus["reddit"]
disorders = dict()
for red in reddit:
    topic = os.path.basename(red).split("_")[0]
    if topic in disorders:
        disorders[topic].append(red)
    else:
        disorders[topic] = [red]

corpus.update(disorders)

# Train corpus specific models
models = dict()
print "Training models..."
for corpus_id,sentences in corpus.iteritems():
    try:
        models[topic] = train_word2vec_model(sentences)
    except:
        print "Error building model for %s" %(topic)
        pass

# Export models to tsv, and save
save_models(models,base_dir)
export_models_tsv(models,base_dir)

# For each set of terms, find overlap with neurosynth model
terms = merge_terms(base_dir,subset=True)
for model_name,model in models.iteritems():
    intersects = vocab_term_intersect(terms,model)
    for tag,ints in intersects.iteritems():
        vs = numpy.unique([x[3] for x in ints]).tolist()
        export_models_tsv({"%s_%s" %(tag,model_name):model},base_dir,vocabs=[vs])

# Export vectors
for model_name,model in models.iteritems():
    print "Processing %s" %(model_name)
    vecs = extract_vectors(model)
    vecs.to_csv("%s/%s.tsv" %(vector_dir,model_name),sep="\t")


# CLASSIFICATION OF DISORDER with reddit text ############################



# NEUROSYNTH #############################################################

# EXPERIMENT 0:
# How does comparing neurosynth maps compare to our matrix?
# We have term relationships defined based on word2vec neural network embeddings
# Neurosynth relationships are defined by pearson comparison of unthresholded reverse inference
# map for that term. How do these two matriccs compare?

# First get all neurosynth terms
relations = terms["neurosynth"]["edges"]
nterms []
for relid,relation in relations.iteritems():
    term1 = relation["source"].replace("neurosynth::","")
    term2 = relation["target"].replace("neurosynth::","")
    if term1 not in nterms:
        nterms.append(term1)
    if term2 not in nterms:
        nterms.append(term2)

wordfish_sims = extract_similarity_matrix(models["neurosynth"])
neurosynth_sims = pandas.DataFrame(columns=wordfish_sims.columns,index=wordfish_sims.columns)
count=0
for relid,relation in relations.iteritems():
    print "%s of %s" %(count,len(relations))
    term1 = relation["source"].replace("neurosynth::","")
    term2 = relation["target"].replace("neurosynth::","")
    neurosynth_sims.loc[term1,term2] = float(relation["value"])
    neurosynth_sims.loc[term2,term1] = float(relation["value"])
    count+=1

wordfish_sims.to_csv("%s/sims_wordfish_neurosynth.tsv" %(analysis_dir),sep="\t")
neurosynth_sims.to_csv("%s/sims_neurosynth_neurosynth.tsv" %(analysis_dir),sep="\t")

# EXPERIMENT 1:
# Can we train a model to predict disorder based on text from reddit?
# Load meta data associated with corpus, this is where we have labels

# stopped here - neurosynth missing edges

# EXPERIMENT 1:
# Do cognitive atlas term relationships hold up in text?
# If our ontology has value, it should be the case that terms (for which we defined relationships) are more similar than other terms for which no relationship is defined.

# Load cognitive atlas terms
intersect_subset = intersects["cognitiveatlas"]
cogat_terms = [x[2] for x in intersect_subset]
neurosynth_terms = [x[3] for x in intersect_subset]
df = pandas.DataFrame()
df["cognitiveatlas"] = cogat_terms
df["neurosynth"] = neurosynth_terms
df=df.drop_duplicates()
df.to_csv("%s/terms/cognitiveatlas/intersect.tsv" %(analysis_dir), sep="\t")

# Find parent/child relationships
relationships = terms["cognitiveatlas"]["edges"]
nodes = terms["cognitiveatlas"]["nodes"]
uids = [x.split("::")[1] for x in nodes.keys()]

# Save the actual relationships, and predicted
predictions = []
for c in range(len(cogat_terms)):
    cogat_term = cogat_terms[c]
    nsyn_term = neurosynth_terms[c]
    concept = get_concept(name=cogat_term).json[0]
    if "relationships" in concept:
        actual_relationships = [x["id"] for x in concept["relationships"]]
        directions = ["%s,%s" %(x["direction"],x["relationship"]) for x in concept["relationships"]]
        actual_relationships = [nodes["cognitiveatlas::%s" %x]["name"] for x in actual_relationships]
        predicted_relationships = model.most_similar(nsyn_term, topn=len(actual_relationships))
        predictions.append((cogat_term,nsyn_term,actual_relationships,directions,predicted_relationships))


# We will look up the cogat_name, and then match to nsynth
cogat_names = [x["name"] for x in nodes.values() if x in df.cognitiveatlas]
nsyn_names [df.neurosynth[df.cognitiveatlas==x] for x in cogat_names]

# It will be faster to use cognitiveatlas api directly without a database
from cognitiveatlas import get_concept
# Save the actual relationships, and predicted
actual = dict()
predicted = dict()
for uid in uids:
    concept = get_concept(id=uid).json[0]
    if "relationships" in concept:
        actual_relationships = [x["id"] for x in concept["relationships"]]
        predicted_relationships = model.most_similar(nodes[], topn=len(actual_relationships))
[('queen', 0.5359965)]
 
 
# "boy" is to "father" as "girl" is to ...?
model.most_similar(['girl', 'father'], ['boy'], topn=3)
[('mother', 0.61849487), ('wife', 0.57972813), ('daughter', 0.56296098)]

more_examples = ["he his she", "big bigger bad", "going went being"]
for example in more_examples:
    a, b, x = example.split()
    predicted = model.most_similar([x, b], [a])[0][0]
    print "'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted)
#'he' is to 'his' as 'she' is to 'her'
#'big' is to 'bigger' as 'bad' is to 'worse'
#'going' is to 'went' as 'being' is to 'was'
 
# which word doesn't go with the others?
model.doesnt_match("breakfast cereal dinner lunch".split())
'cereal'


# EXPERIMENT 2:
# Combined concepts
# If cognitive atlas labeling is good, then a term with two parent concepts should be more similar to the mean of the child concepts than other concepts.
# What would the ontology relationships look like if we derived them from text alone?

#TODO:
# finish experiments above, including classification and comparison with neurosynth
# make interface to visualize 1) word embeddings, 2) comparing a word across corpus
