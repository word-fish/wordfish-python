'''
terms.py

part of the deepdive python package: parsing of term data structures into formats for deepdive
this set of functions works with different plugins (in plugins folder) to produce input terminologies
to search for in corpus

'''
import nltk
import pandas

def download_nltk():
    '''download_nltk
    download nltk to home
    '''
    home=os.environ["HOME"]
    download_dir = "%s/nltk_data" %home
    print "Downloading nltk to %s" %(download_dir)
    if not os.path.exists(download_dir):
        import nltk
        nltk.download('all')
    return "%s/nltk_data" %(home)


def save_terms(input_terms,output_dir):
    print "TODOWRITEME"
