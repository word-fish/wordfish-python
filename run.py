#!/usr/bin/python

# IMPORTS #########################################################################
import os
import sys
from wordfish.vm import init_scripts, make_plugin_folders
from wordfish.utils import make_directory
from wordfish.terms import download_nltk

# DIRECTORIES #####################################################################
analysis_dir = sys.argv[1]
# /work/02092/vsochat/wrangler/
#corenlp_dir="/%s/SOFTWARE/stanford-corenlp-full-2015-04-20" %(analysis_dir)
corpus_output = make_directory("%s/corpus" %(analysis_dir))
terms_output = make_directory("%s/terms" %(analysis_dir))
scripts_directory = make_directory("%s/scripts" %(analysis_dir))

# INIT FUNCTIONS ##################################################################
# These are fine to re-run, if already done will not cause harm
download_nltk()
make_plugin_folders(analysis_dir)
init_scripts(scripts_directory,analysis_dir)

print "\n\n\n################################ WORDFISH ################################\n\nApplication at %s\n\nScripts are generated in scripts folder. Use run_slurm.py (and check that the parameters are ok) to submit slurm jobs as follows:\n\n  python run_slurm.py run_terms_extractions.py\n\nLaunch is recommended as another method, see: https://github.com/vsoch/poldracklab-launch\n\nExtractions of terms, corpus, and relationships can be done in parallel, but must be done before run_analysis_setup.job [NOT YET WRITTEN] and before run_inference.job [NOT YET WRITTEN]" %analysis_dir
