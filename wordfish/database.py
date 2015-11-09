'''
database.py

part of the wordfish python package: extracting relationships of terms from corpus


'''

import os

def import_files(files,table_name):
    if isinstance(files,str): 
        files = [files]
    for import_file in files:
        if os.path.exists(import_file):
            os.system('deepdive sql "COPY %s FROM STDIN CSV" <%s' %(table_name,import_file))

def create_all_tables():
    create_mentions_table()
    create_sentences(table)
    create_features_table()
    create_inference_table()


def create_table():
    print "WRITEME"


def make_mentions_table():
    print "WRITEME"


def make_sentences_table():
    print "WRITEME"

