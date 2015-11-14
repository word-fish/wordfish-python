#!/usr/bin/env bash

# install.sh

# This is the single script that the user should run after generating this
# directory to generate all inputs for the pipeline. The only input argument
# is a project directory of interest, WORK. If the application
# is deployed to a virtual machine (either local or on aws) these
# installation steps will not be necessary. User instructions will
# be provided in documentation to give details to this.

if [ $# -eq 0 ]
  then
    echo "Please provide a base project folder as the only input argument."
    exit
fi

WORK=$1

# Add WORDFISH_HOME to bash rc
echo "export WORDFISH_HOME=$WORK" >> .bashrc
echo "export WORDFISH_HOME=$WORK" >> .env

# Installation python package
python setup.py install --user

# Run the script to call the application
python run.py $WORK
