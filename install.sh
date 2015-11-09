#!/usr/bin/env bash

# install.sh

# This is the single script that the user should run after generating this
# directory to generate all inputs for the pipeline. The only input argument
# is a project directory of interest, WORK. If the application
# is deployed to a virtual machine (either local or on aws) these
# installation steps will not be necessary. User instructions will
# be provided in documentation to give details to this.


# VARIABLES FILLED IN FROM DEEPDIVE-PYTHON
WORK=$1

# Installation python package
python setup.py install --user

# Run the script to call the application
python run.py $WORK
