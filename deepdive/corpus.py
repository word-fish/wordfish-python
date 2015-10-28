'''
corpus.py

part of the deepdive python package: parsing of term data structures into formats for deepdive
this set of functions works with different plugins (in plugins folder) to produce input corpus
for parsing.

'''
import nltk
import pandas

# First download nltk stuffs
def download_nltk():
    home=os.environ["HOME"]
    if not os.path.exists("%s/nltk_data" %home):
        import nltk
        nltk.download('all')
    return "%s/nltk_data" %(home)


# Not sure yet how I want to do this

#TODO: This was coded for neurosynth, needs to be generic
def write_articles(output_file):
    '''write_articles
    Write articles to file

    88390|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    88390|"<text><p>sentence1</p><p>sentence2</p><p></text>"
    We should use utf-8 http://www.postgresql.org/docs/9.0/static/multibyte.html
 
    '''
    filey = open(output_file,"wb")
    count = 0 
    for pmid, article in articles.iteritems():
        print "Parsing %s of %s" %(count,len(articles))
        filey.write('%s|"<text>' %pmid)
        abstract = article.getAbstract()
        blob = TextBlob(abstract)
        for sentence in blob.sentences:
            sentence = '<p>%s</p>' %sentence.raw.replace("\t","").replace("|"," ").replace("\n","").replace("\r","")
            filey.write(sentence.replace("}","").replace("{","").encode("utf-8"))
        filey.write('</text>"\n')
        count = count+1 
    filey.close()


