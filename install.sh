#!/usr/bin/env bash
'''
install.sh

This is the single script that the user should run after generating this
directory to generate all inputs for the pipeline. The only input argument
is a project directory of interest, WORK. If the application
is deployed to a virtual machine (either local or on aws) these
installation steps will not be necessary. User instructions will
be provided in documentation to give details to this.

'''

# VARIABLES FILLED IN FROM DEEPDIVE-PYTHON
WORK=$1
INSTALL_CORENLP="True" 
INSTALL_DEEPDIVE="True" 

# Installation python package
python setup.py install --user

# Set up software directory in work
CURRENT_DIRECTORY=$PWD
cd $WORK
mkdir SOFTWARE
mkdir APP
mkdir APP/input
cd $CURRENT_DIRECTORY

if [[ $INSTALL_CORENLP == "True" ]] ; then
    # Install core NLP
    cd $WORK/SOFTWARE
    wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-04-20.zip
    unzip stanford-corenlp-full-2015-04-20.zip

    # http://nlp.stanford.edu/software/basic-compiling.txt
    cd stanford-corenlp-full-2015-04-20
    mkdir src
    cd src
    jar -xf ../stanford-corenlp-3.5.2-sources.jar
    cd $WORK/SOFTWARE
    wget http://www.us.apache.org/dist/ant/binaries/apache-ant-1.9.6-bin.zip
    unzip apache-ant-1.9.6-bin.zip 
    cd $WORK/SOFTWARE/stanford-corenlp-full-2015-04-20
    module load java64/1.8.0
    $WORK/apache-ant-1.9.6/bin/ant

    # Install python wrapper
    cd $WORK/SOFTWARE
    git clone https://github.com/brendano/stanford_corenlp_pywrapper
    cd stanford_corenlp_pywrapper
    pip install . --user

    echo "# Stanford CoreNLP/Ant" >> ~/.bashrc
    echo "module load java64/1.8.0" >> ~/.bashrc
    echo "export PATH=$PATH:$WORK/SOFTWARE/stanford-corenlp-full-2015-04-20" >> ~/.bashrc
    echo "export PATH=$PATH:$WORK/SOFTWARE/apache-ant-1.9.6-bin/bin" >> ~/.bashrc
    cd $CURRENT_DIRECTORY
fi


# INSTALL DEEPDIVE
if [[ $INSTALL_DEEPDIVE == "True" ]] ; then

    cd $WORK/SOFTWARE
    git clone https://github.com/HazyResearch/deepdive.git
    cd deepdive
    make 
    export PATH="~/local/bin:$PATH"

    # Add to bashrc
    echo "export PATH=~/local/bin:$PATH" >> ~/.bashrc
    echo "export DEEPDIVE_HOME=$WORK/SOFTWARE/deepdive" ~/.bashrc    

    make install
    source ~/.bashrc

fi

# Run the script to call the application
python run.py $WORK
