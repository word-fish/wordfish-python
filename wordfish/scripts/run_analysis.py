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
    - Build classifiers to predict labels from vectors

'''

# First train simple word2vec model with different corpus
from wordfish.analysis import build_models, save_models, export_models_tsv, load_models, extract_similarity_matrix, export_vectors, featurize_to_corpus
from wordfish.models import build_svm
from wordfish.corpus import get_corpus, get_meta, subset_corpus
from wordfish.terms import get_terms
from wordfish.utils import mkdir
import os

base_dir = os.environ["WORDFISH_HOME"]

# Setup analysis output directories
analysis_dir = mkdir("%s/analysis" %(base_dir))
model_dir = mkdir("%s/models" %(analysis_dir))
vector_dir = mkdir("%s/vectors" %(analysis_dir))

# Generate more specific corpus by way of file naming scheme
corpus = get_corpus(base_dir)
reddit = corpus["reddit"]
disorders = subset_corpus(reddit)
corpus.update(disorders)


# Train corpus specific models
models = build_models(corpus)

# Export models to tsv, export vectors, and save
save_models(models,base_dir)
export_models_tsv(models,base_dir)
export_vectors(models,output_dir=vector_dir)


### Working with models #######################################################################

# Find the most similar words for a query word:
model = load_models(base_dir)["neurosynth"]
model.most_similar("anxiety")
# [('aggression', 0.77308839559555054), 
#   ('stress', 0.74644440412521362), 
#   ('personality', 0.73549789190292358), 
#   ('excessive', 0.73344630002975464), 
#   ('anhedonia', 0.73305755853652954), 
#   ('rumination', 0.71992391347885132), 
#   ('distress', 0.7141801118850708), 
#   ('aggressive', 0.7049030065536499), 
#   ('craving', 0.70202392339706421), 
#   ('trait', 0.69775849580764771)]

# Corpus context is important
model = load_models(base_dir)["reddit"]
model.most_similar("anxiety")
# [('crippling', 0.64760375022888184), 
# ('agoraphobia', 0.63730186223983765), 
# ('generalized', 0.61023455858230591), 
# ('gad', 0.59278655052185059), 
# ('hypervigilance', 0.57659250497817993), 
# ('bouts', 0.56644737720489502), 
# ('depression', 0.55617612600326538), 
# ('ibs', 0.54766887426376343), 
# ('irritability', 0.53977066278457642), 
# ('ocd', 0.51580017805099487)]

# perform addition and subtraction with vectors
model.most_similar(positive=['anxiety',"food"])
# [('ibs', 0.50205761194229126), 
# ('undereating', 0.50146859884262085), 
# ('boredom', 0.49470821022987366), 
# ('overeating', 0.48451068997383118), 
# ('foods', 0.47561675310134888), 
# ('cravings', 0.47019645571708679), 
# ('appetite', 0.46869537234306335), 
# ('bingeing', 0.45969703793525696), 
# ('binges', 0.44506731629371643), 
# ('crippling', 0.4397256076335907)]

model.most_similar(positive=['bipolar'], negative=['manic'])
# [('nos', 0.36669495701789856), 
# ('adhd', 0.36485755443572998), 
# ('autism', 0.36115738749504089), 
# ('spd', 0.34954413771629333), 
# ('cptsd', 0.34814098477363586), 
# ('asperger', 0.34269329905509949), ('schizotypal', 0.34181860089302063), ('pi', 0.33561226725578308), ('qualified', 0.33355745673179626), ('diagnoses', 0.32854354381561279)]

model.similarity("anxiety","depression")
#0.67751728687122414

model.doesnt_match(["child","autism","depression","rett","cdd","young"])
#'depression'

# Get the raw vector for a word
model["depression"]

# Extract a pairwise similarity matrix
wordfish_sims = extract_similarity_matrix(models["neurosynth"])



# Classication ############################################################################
# Predict neurosynth abstract labels with pubmed neurosynth corpus

# Load model and meta for neurosynth, meaning labels for each text
model = load_models(base_dir,"neurosynth")["neurosynth"]
meta = get_meta(base_dir)["neurosynth"]
vectors,labels = featurize_to_corpus(model,meta)
classifiers = build_svm(vectors=vectors,labels=labels,kernel="linear")
