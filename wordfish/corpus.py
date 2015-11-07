'''
corpus.py

part of the wordfish python package: extracting relationships of terms from corpus
this set of functions works with different plugins (in plugins folder) to produce input corpus
for parsing.

'''
import pandas

def save_sentences(articles,output_dir="."):
    '''save_sentences: 
    parses a dictionary with articles and sentences into output sentence files
    Parameters
    ==========
    articles: list or dict
        a list or dictionary of articles to parse and save to sentences.txt files.
        If you have a meaningful unique ID, provide a dictionary with the UID as key
        If not, provide a list and an integer will be generated instead.
    output_dir: path
        full path that corresponds to the plugins specific directory under "corpus"
        eg $WORK/corpus/neurosynth
    '''
    if isinstance(articles,dict):
        for uid, text in articles.iteritems():
            save_sentences_single(uid,text)

    elif isinstance(articles,list):
        for uid in range(len(articles)):
            save_sentences_single(uid,articles[uid],output_dir)

def save_sentences_single(uid,text,output_dir,remove_non_english_chars=True):
    '''save_sentence_single
    Write sentences to file

    88390|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    88391|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    We should use utf-8 http://www.postgresql.org/docs/9.0/static/multibyte.html
 
    Parameters
    ==========
    uid: int or string
        a unique ID for the article
    text: str
        raw text of the article    
    output_dir: path
        full path to a plugins corpus directory
    '''
    output_file = "%s_sentences.txt" %(output_dir)
    filey = open(output_file,"wb")
    filey.write('%s|"<text>' %uid)
    blob = TextBlob(text)
    for sentence in blob.sentences:
        sentence = '<p>%s</p>' %sentence.raw.replace("\t","").replace("|"," ").replace("\n","").replace("\r","")
        filey.write(sentence.replace("}","").replace("{","").encode("utf-8"))
    filey.write('</text>"\n')
    filey.close()