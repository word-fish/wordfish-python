'''
terms.py

part of the wordfish python package: extracting relationships of terms from corpus

this set of functions works with different plugins (in plugins folder) to produce input terminologies
to search for in corpus

'''
from wordfish.utils import save_pretty_json, find_directories, read_json
from uuid import uuid4
import pandas
import nltk
import os

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
        if tup[0].lower() and tup[1].lower() in ids:
            links.append({"source":tup[0],"target":tup[1],"value":tup[2]})

    result = {"edges":links}
    if output_dir is not None:
        tmp = save_pretty_json(result,"%s/term_relationships.json" %(output_dir))
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
        for t in range(len(input_terms)):
            term = input_terms[t]
            nodes.append({"name":term.lower(),"uid":str(t)})
            ids.append(term.lower())
    elif isinstance(input_terms,dict):
        for node, meta in input_terms.iteritems():
            meta["uid"] = str(node).lower()
            nodes.append(meta)
            ids.append(str(node).lower())
    else:
        print "Invalid input_terms, must be str, dict, or list."
        return

    result = {"nodes":nodes}
    if output_dir is not None:
        tmp = save_pretty_json(result,"%s/terms.json" %(output_dir))
    return result


def merge_terms(analysis_dir,subset=False):
    '''
    For all terms defined, and relationships for the terms, parse into a single data structure
    This (maybe) won't work for larger datasets (we will use a database) but it will for testing.

        nodes:

            {"[plugin]::[uid]":[node]}

    Parameters
    ==========
    analysis_dir: path
        full path to analysis directory
    subset: boolean
        if True, returns terms in dictionary based on source tag. Default==False    
    '''

    nodes = dict()
    edges = dict()

    terms_dir = "%s/terms" %(os.path.abspath(analysis_dir))
    if os.path.exists(terms_dir):
        term_plugins = find_directories(terms_dir)


        nodes = dict()
        edges = dict()
        results = dict()

        for term_plugin in term_plugins:
            plugin_name = os.path.basename(term_plugin)

            if subset:
                nodes = dict()
                edges = dict()

            # Here we parse together terms
            if os.path.exists("%s/terms.json" %term_plugin):
                terms_json = read_json("%s/terms.json" %term_plugin)["nodes"]
                for node in terms_json:
                    if "uid" in node:
                        uid = "%s::%s" %(plugin_name,node["uid"])
                    else:
                        feature_name = node["name"].replace(" ","_")
                        uid = "%s::%s" %(plugin_name,feature_name) 
                    nodes[uid] = node

            # Here we parse together relationships
            # Currently only supported for terms within the same family
            if os.path.exists("%s/term_relationships.json" %term_plugin):
                terms_json = read_json("%s/term_relationships.json" %term_plugin)["edges"]
                for relation in terms_json:
                    uid_1 = "%s::%s" %(plugin_name,relation["source"])
                    uid_2 = "%s::%s" %(plugin_name,relation["target"])
                    relation_uid = "%s<>%s" %(uid_1,uid_2)
                    edges[relation_uid] = {"source": uid_1,
                                           "target": uid_2,
                                           "value": relation["value"]}

            result = {"nodes":nodes,"edges":edges}
            if subset:
                results[plugin_name] = result
    
    if subset:
        result = results
    else:
        result = {"all":result}
    # Return the result to user with all edges and nodes defined
    if analysis_dir is not None:
        tmp = save_pretty_json(result,"%s/terms/terms.json" %(analysis_dir))
    return result
