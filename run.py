#!/usr/bin/python

# IMPORTS #########################################################################
import os
import sys
from wordfish.utils import make_directory, init_scripts
from wordfish.terms import download_nltk

# PLUGIN IMPORTS APPENDED HERE
import wordfish.plugins.neurosynth as neurosynth

# DIRECTORIES #####################################################################
analysis_dir = sys.argv[1]
# /work/02092/vsochat/wrangler/
#corenlp_dir="/%s/SOFTWARE/stanford-corenlp-full-2015-04-20" %(analysis_dir)
corpus_output = make_directory("%s/corpus" %(analysis_dir))
terms_output = make_directory("%s/terms" %(analysis_dir))
jobs_directory = make_directory("%s/jobs" %(analysis_dir))
scripts_directory = make_directory("%s/scripts" %(analysis_dir))

# INIT FUNCTIONS ##################################################################
# These are fine to re-run, if already done will not cause harm
download_nltk()
init_scripts()

# CORPUS ##########################################################################

# CORPUS EXTRACTION APPENDED HERE
neurosynth.extract_text(output_dir="%s/neurosynth" %corpus_output)


# TERMS ###########################################################################

# TERMINOLOGY EXTRACTION APPENDED HERE
neurosynth.extract_terms(output_file="%s/neurosynth_terms.json" %corpus_output)


# INFERENCE ########################################################################

