#!/usr/bin/python

# IMPORTS #########################################################################
import os
import sys
from wordfish.vm import init_scripts, make_plugin_folders
from wordfish.utils import make_directory
from wordfish.terms import download_nltk

# DIRECTORIES #####################################################################
if len(sys.argv) < 2:
    print 'Please provide a base project folder path as the only input argument.'
    sys.exit(32)
analysis_dir = os.path.abspath(sys.argv[1])
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

print "\n\n\n################################ WORDFISH ################################\n\nApplication at %s\n\nScripts are generated in scripts folder. First open run_slurm.py to check that the parameters are ok. Then you will run a script to generate jobs for each plugin:\n\n python run_slurm.py run_first.job\n\nThis will generate a list of commands to be run for each plugin that you have selected, and you should submit the list to your cluster (or run with launch) to complete all the extractions:\n\npython run_slurm.py run_extractions_reddit.py.\n\nLaunch is recommended as another method, see: https://github.com/vsoch/poldracklab-launch\n\nOnce corpus, terms, and relationships are extracted, you can run run_analysis.py [NOT YET DEVELOPED]." %analysis_dir
