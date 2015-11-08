'''
terms.py

part of the wordfish python package: extracting relationships of terms from corpus

this set of functions works with different plugins (in plugins folder) to produce input terminologies
to search for in corpus

'''
import nltk
import pandas
from wordfish.utils import save_pretty_json

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


def save_relationships(input_terms,relationships,output_dir=None):
    '''save_relationships
    Parameters
    =========
    input_terms: list,dict
        a list or dictionary of terms. If relationships exist between terms,
        relationships should be defined, with key as the unique ID for the terms.
        if meta data are used to describe the input_terms, provide the input_terms
        as a dictionary with a dictionary to define {"meta_label":"meta_value"}
     output_dir: path
        path to save output. If none, will just return json dictionary
    relationships: list of tuples [(source,target,relation)]
        if defined, all keys must be in input_terms. Not yet decided what a "relation" should be, but for now assume you can have it be a string or number.
    Returns
    =======
    terms: dict
        dictionary structure with the following format (parallel to what many d3
        algorithms use to define graphs)

        {
         "links": [{"source":"node1","target":"node2","value":0.5}]
        }

    '''
    # Not sure why anyone would do this, but might as well check
    links = []
    ids = []
    if isinstance(input_terms,str):
        input_terms = [input_terms]
    if isinstance(input_terms,list):
        input_terms = [x.lower() for x in input_terms]
        for term in input_terms:
            ids.append(term.lower())
    elif isinstance(input_terms,dict):
        for node, meta in input_terms.iteritems():
            ids.append(node.lower())
    else:
        print "Invalid input_terms, must be str, dict, or list."
        return

    # Save relationships
    for tup in relationships:
        if tup[0].lower() or tup[1].lower() not in ids:
            print "Entry %s has nodes not defined in input_terms!" %(tup)
            return
        links.append({"source":tup[0],"target":tup[1],"value":tup[2]})

    result = {"links":links}
    if output_dir is not None:
        save_pretty_json(result,"%s/%s_relationships.json" %(output_dir))
    return result

def save_terms(input_terms,output_dir=None):
    '''save_terms
    Parameters
    =========
    input_terms: list,dict
        a list or dictionary of terms. if meta data are used to describe the  input_terms, provide the input_terms as a dictionary with a dictionary to define {"meta_label":"meta_value"}
     output_dir: path
        path to save output. If none, will just return json dictionary
    Returns
    =======
    links: dict
        dictionary structure with the following format (parallel to what many d3
        algorithms use to define graphs)

        {"nodes":[{"name":"node1"},
                 {"name":"node2"}],
         }

    '''
    # Not sure why anyone would do this, but might as well check
    nodes = []
    ids = []
    if isinstance(input_terms,str):
        input_terms = [input_terms]
    if isinstance(input_terms,list):
        input_terms = [x.lower() for x in input_terms]
        for term in input_terms:
            nodes.append({"name":term.lower()})
            ids.append(term.lower())
    elif isinstance(input_terms,dict):
        for node, meta in input_terms.iteritems():
            meta["uid"] = node.lower()
            nodes.append(meta)
            ids.append(node.lower())
    else:
        print "Invalid input_terms, must be str, dict, or list."
        return

    result = {"nodes":nodes}
    if output_dir is not None:
            save_pretty_json(result,"%s/terms.json" %(output_dir))
    return result
