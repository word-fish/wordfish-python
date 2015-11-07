'''
parser.py

part of the deepdive python package: parsing of corpus inputs through corenlp
pipeline.

'''

from stanford_corenlp_pywrapper import CoreNLP
import sys
import os

def get_parser(corenlp_jars):
    #TODO: we can add specific annotators here! Let's do generic for now
    proc = CoreNLP(configdict={'annotators':'tokenize, ssplit, pos, parse, lemma, ner'},
           output_types=["pos","parse"], 
           corenlp_jars=["%s/*" %(corenlp_jars)])
    return proc

def prepare_corenlp(terms_input,corpus_input,scripts_directory,jobs_directory):
    '''prepare_corenlp
    prints commands to a jobfile to run the stanford parser over a set of inputs
    Parameters
    ==========
    terms_input: path
        full path with plugin terms subdirectories
    corpus_input: path
        full path with plugin corpus subdirectories
    jobs_directory: path
        path to directory to save job
    scripts_directory: path
        path to directory with analysis scripts
    '''


def run_stanford_parser(input_file,output_file,corenlp_dir):
    '''run_stanford_parser: 
    runs corenlp parser over a single text file
    Parameters
    ==========
    input_file: file path     
        format expected to be:

        "12345|<text><p>hello this is text, sentence one!</p><p>sentence two!</p></text>"

        where 12345 is a unique id (for the corpus), the text is between <text>,
        and sentences are between <p></p>
    output_file: file path
        the file to write the parsed output to, typically is something like
        $WORK/extractions/corpus1_12345_extractions.txt
    corenlp_dir: directory path
        full path to corenlp jars files

    Returns
    =======
    output_file: text file
        
        Writing to output file, format should look like
        101226,
        A spokesman at the British Embassy here declined to comment .,
        "{A,spokesman,at,the,British,Embassy,here,declined,to,comment,.}",
        "{a,spokesman,at,the,British,Embassy,here,decline,to,comment,.}",
        "{DT,NN,IN,DT,NNP,NNP,RB,VBD,TO,VB,.}",
        "{""root(ROOT-0, declined-8)"",""det(spokesman-2, A-1)"",""nsubj(declined-8, spokesman-2)"",""det(Embassy-6, the-4)"",""nn(Embassy-6, British-5)"",""prep_at(spokesman-2, Embassy-6)"",""advmod(declined-8, here-7)"",""aux(comment-10, to-9)"",""xcomp(declined-8, comment-10)""}",
        "{O,O,O,O,ORGANIZATION,ORGANIZATION,O,O,O,O,O}",
         9,
         101226@9
    '''
    # Prepare the parser
    proc = get_parser(corenlp_dir)

    # Any errors will have entries written to an error file for inspection
    # TODO: user interface for parsing files with errors to check why
    error_file = output_file.replace(".txt",".err")
    filey = open(input_file,"rb")
    lines = filey.readlines()[0]
    filey.close()

    article_id,text = lines.split("|")
    text =  text.replace("</text>","").replace("<text>","").strip("\n").replace('"',"")
    paragraphs = text.split("<p>")
    paragraphs = [p for p in paragraphs if p]

    filey = open(output_file,"w")

    for p in range(0,len(paragraphs)):
        paratext = paragraphs[p].replace("<p>","").replace("</p>","").replace("\t"," ").replace('"',"''").replace(",","")
        sentence_id = "%s@%s" %(article_id,p)
        try:
            nlp = proc.parse_doc(paratext)
            wordslist = nlp["sentences"][0]["tokens"]
            text = '"%s"' %(",".join(wordslist))
            
            # All commas must be replaced with "" from here on
            wordslist = [x.replace(',','""') for x in wordslist]
            words = "{%s}" %(",".join(wordslist))
            lemmas = [x.replace(',','""') for x in nlp["sentences"][0]["lemmas"]]
            lemmas = "{%s}" %(",".join(lemmas))
            pos = [x.replace(',','""') for x in nlp["sentences"][0]["pos"]]
            pos = "{%s}" %(",".join(pos))
            ner = "{%s}" %(",".join(nlp["sentences"][0]["ner"]))
           
            # This is a lookup for the terms, using the words
            dependencies = "{%s}" %(",".join(['""%s""' %(dependency_structure(wordslist,x)) for x in nlp["sentences"][0]["deps_cc"]]))
        
            # document_id | sentence | words | lemma | pos_tags | dependencies | ner_tags | sentence_offset | sentence_id 
            for_database = '%s,%s,"%s","%s","%s","%s","%s",%s,%s\n' %(article_id,text,words,lemmas,pos,dependencies,ner,p,sentence_id)
            filey.writelines(for_database)
        except:  
            if not os.path.exists(error_file):
                efiley = open(error_file,"w")
                efiley.writelines("%s|%s\n" %(sentence_id,paratext))

    filey.close()

    if os.path.exists(error_file):
        efiley.close()



def dependency_structure(words,dependency):
    '''dependency_structure
    This is a function to return a dependency structure to input into database
    '''
    word = dependency[0]
    start = dependency[1]
    end = dependency[2]
    structure = word.encode("utf-8") 
    # Indexing starts at 1, so we add 1
    if word == "root":
        structure = "%s(ROOT-%s, %s-%s)" %(structure,start+1,words[end],end+1)
    else:
        structure = "%s(%s-%s, %s-%s)" %(structure,words[start],start+1,words[end],end+1)
    return structure.encode("utf-8")
