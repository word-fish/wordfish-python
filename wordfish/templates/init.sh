#!/usr/bin/env bash

set -eux
cd "$(dirname "$0")"  # move into the directory where this script is

# SECTIION FOR OBTAINING CORPUS
[SUB_CORPUS_SUB]

# PREPARE STANFORD NLP PARSER
bash ../slurm/0.prep_core_nlp.sh

# We will use launcher
#module use /home/02092/vsochat/SCRIPT/modules/launch
#module load poldracklablaunch

# Create sentences table
deepdive sql "
  CREATE TABLE sentences(
    document_id text,
    sentence text,
    words text[],
    lemma text[],
    pos_tags text[],
    dependencies text[],
    ner_tags text[],
    sentence_offset bigint,
    sentence_id text
);
"

# Extract sentences, and launch!
python ../slurm/1.run_nlp_parser.sh

# Test
#python /home/02092/vsochat/SCRIPT/deepdive/neurosynth-nlp/slurm/1.nlp_parser.py /work/02092/vsochat/wrangler/DATA/NEUROSYNTH-NLP/corenlp/sentences/25505380_sentences.txt /work/02092/vsochat/wrangler/DATA/NEUROSYNTH-NLP/corenlp/extractions/25505380_extractions.txt

# Launcher script is already prepared
sbatch ../slurm/templates/nlpextract.slurm
# (this will also add sentences to the database)

# Add sentences to the database
#python ../slurm/2.import_sentences.py

# deepdive sql "select count(*) from sentences"
# count 
#-------
# 87044
# (1 row)


# If you get this error:
# ERROR:  must be superuser to create procedural language "plpythonu"
# You or an admin must do:
# sudo apt-get install postgresql-plpython
# deepdive sql 'CREATE LANGUAGE plpythonu;'

# If the compiled brain regions file doesn't exist, create it
if ! [[ -e ../udf/NER/brain_regions.json ]]; then
    echo "Generating compiled brain regions json..."
    python ../udf/NER/compile_brain_regions.py ../udf/NER/brain_regions.json "../udf/NER/aba-syn.xml,../udf/NER/bams2004swanson-syn.xml"
fi

# Create tables for mentions
deepdive sql "
  CREATE TABLE concept_mentions(
    sentence_id text,
    start_position int,
    length int,
    text text,
    mention_id text
);
"

deepdive sql "
  CREATE TABLE region_mentions(
    sentence_id text,
    start_position int,
    length int,
    text text,
    mention_id text 
  );
"

# Export data to extract mentions of concepts and regions
# STOPPED HERE - maybe get start and end index of sentences.csv?
deepdive sql "COPY (SELECT sentence_id, words From sentences) TO STDOUT WITH CSV;" >> sentences.csv
python ../slurm/3.run_extract_mentions.py

# Launcher scripts are already prepared
sbatch ../slurm/templates/extract_concepts.slurm
sbatch ../slurm/templates/extract_regions.slurm

# Now we will extract candidates for has_cognitive_process relations, 
# the simplest thing to do is have them in the same sentence

# this is for concept --> concept associations
# we can train this using the cognitive atlas
# however we will need negative assertions as well

# this is for region --> concept associations 
deepdive sql "
CREATE TABLE has_cognitive_concept(
    region_id text,
    concept_id text,
    sentence_id text,
    description text,
    is_true boolean,
    relation_id text,
    id bigint 
);
"

deepdive sql "
CREATE TABLE has_related_concept(
  concept1_id text,
  concept2_id text,
  sentence_id text,
  description text,
  is_true boolean,
  relation_id text, 
  id bigint
);
"

deepdive sql "
CREATE TABLE has_cognitive_concept_features(
  relation_id text,
  feature text
);
"

deepdive sql "
CREATE TABLE has_related_concept_features(
  relation_id text,
  feature text
);
"

# First try extracting related concepts - we only need concept_mentions for this
# This will also extract candidates and features of the related concepts
DEEPDIVE_JDBC_URL='jdbc:postgresql://db1.wrangler.tacc.utexas.edu:5432/deepdive_spouse?ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory' deepdive run has_related_concept

# STOPPED HERE - there is an error (null iD)
DEEPDIVE_JDBC_URL='jdbc:postgresql://db1.wrangler.tacc.utexas.edu:5432/deepdive_spouse?ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory' deepdive run has_related_concept_inference

# Get BrainDump
$DEEPDIVE_HOME/examples/tutorial_example/step1-basic/get-braindump.sh

# Now we need to use neurosynth to generate training data for region / concept relations

# We will set a threshold of >.75 to define a relationship as "TRUE" and <=.25 as FALSE
