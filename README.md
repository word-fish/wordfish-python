# wordfish-python

  >>   If pulling a thread of meaning from woven text <br>
  >>   is that which your heart does wish. <br>
  >>   Not so absurd or seemingly complex,  <br>
  >>   if you befriend a tiny word fish. <br>

<div style="float: right">
    <img src="doc/img/wordfish_smile.png" alt="wordfish" title="Wordfish" style="float:right"/>
</div>

Choose your input corpus, terminologies, and deployment environment, and an application will be generated to use deep learning to extract relationships between terms of interest, and classify new texty things. Custom plugins will allow for dynamic generation of corpus and terminologies from data structures and standards of choice from [wordfish-plugins](http://www.github.com/vsoch/wordfish-plugins) You can have experience with coding (and use the functions in the module as you wish), or no experience at all, and let the interactive web interface walk you through generation of your application. This will ideally be able to generate single instances of analysis applications, and an instance that we can deploy on the cloud (and integrate into a collaborative, cloud-based tool for many researchers to use).

[will eventually be here](https://pypi.python.org/pypi/wordfish)

** under development! ** not ready for use!


### 0. Install the tool

      pip install git+git://github.com/vsoch/wordfish-python.git


### 1. Generate your application

Call the tool to configure your application:

    wordfish


![view1](example/img/view1.png)

Setup your database, or have the tool set it up for you.
![view2](example/img/view2.png)

Select from the available corpus.
![view3](example/img/view3.png)

Select your terminologies.
![view4](example/img/view4.png)

A custom application is generated for you!
![view5](example/img/view5.png)


This will produce a folder for you to drop in your cluster environment.

### 2. Install dependencies

Drop the folder into your home directory of your cluster environment. Run the install script to install deepdive, corenlp, and the package itself. The first (and only) argument is the project directory where you want your data and outputs to live.

      
      WORK=/scratch/users/vsochat/wordfish-nlp
      bash install.sh $WORK
      

### 3. Prepare cluster jobs

After installations are complete, this install script will also call `run.py`, which will do preliminary work preparing all input files and corpus to do extractions. This is just preparing job files and is not hugely computationally intensive, and could probably be done on a screen on a home node. If you feel antsy about it, you can connect to a dev node. If you look at the run.py script, you will see commands appended to prepare the corpus and terms that you specified. This is going to generate the following file structure in your project folder (and files that will eventually be produced are shown):

      WORK
          SOFTWARE
              wordfish
          APP
              corpus
                  corpus1
                      12345_sentences.txt
                      12346_sentences.txt
                  corpus2
                      12345_sentences.txt
                      12346_sentences.txt
              terms
                  terms1
                  terms2

              jobs
                  run1_corenlp.txt
                  run4_features.txt
                  run5_inference.txt
              scripts

The folders are generated dynamically for each corpus and terms plugin based on the "tag" variable in the plugin's config. The tag names for the plugins are the only unique requirement, and the creator of the plugin can either decide a meaningful unique id for the sentences output, or not specify and let deepdive.corpus decide. This doesn't matter until all extractions are complete, at which time a unique ID is assigned to the files.

### 4. Run cluster jobs

Most of these files are not generated with the run.py script - the run.py script generates jobs to be run in parallel to produce these files (in the "jobs" directory), and some of these jobs require generic scripts (in the "scripts" directory) that use deepdive-python functions in the cluster environment. The high level idea is that we package each step of the pipeline into a set of jobs that can be run in parallel (specified as lines in each file in the "jobs" directory). This means that after running run.py, you will have sentenves for each corpus, a term data structure for each data structure, and a folder filled with "jobs" to submit to a cluster, and run in the order specified when the previous step has completed. This package provides functions for running these commands in a slurm (submission) environment, or a launch system (all at once) (details to follow).

(Note: For now, since obtaining the corpus and parsing to sentences is not computationally or time intensive, this is also done by the run script, but this could also be moved to be a cluster task.)

** under development **
more details to come as they are figured out, coded, etc.



#### Deployment Options

##### Virtual Machine
The user can select to deploy to a vagrant-vm, or amazon-aws virtual machine. This means (for now) that all processing will be done in serial (or with a small job manager). This means that deepdive and an appropriate database can be configured and set up for the user, or he/she can specify a different database.

##### Cluster
The user can select to deploy an analysis application, meaning a zipped up folder with an install script to deploy in a cluster environment. I will start with two options for job managers: SLURM, and "launch" (meaning using a grid system set up with a SLURM cluster). For launch, commands will be executed as lines in a single file. For SLURM, commands will be sbatch commands submit from a particular user when jobs are allowed.

#### Local
If the user already has deepdive, the same zipped up folder can be deployed locally (sans cluster submission), but I don't see why anyone would want to do this.

### Standards
Standards will be different kinds of file structures that the module will know how to parse. Including:

- owl: a structured language (ontology) is an extension of an RDF file, and an obvious candidate to define different mentions.
- nifti: is a brainmap image, for an atlas or brain map (also structured, an XML file and nifti image)

### Plugins 
Plugins will be resources from which to derive corpus and/or terminology (terms). Initial plugins will include the following:

- wordnet: people might just want a subset of "normal word" terms deemed important by way of relationships in wordnet
- reddit: in my mind, is a rich source of behavioral phenotypes
- pubmed: many plugins will require downloading abstracts or full text from here
- cognitiveatlas: an ontology of cognitive concepts, tasks, disorders
- neurosynth: database of significant coordinates extracted from a set of pubmed abstracts, and associated features (terms)
- neurovault: database of statistical brain maps (corpus)
