'''
plugin.py

part of the wordfish python package: extracting relationships of terms from corpus
this set of functions finds and validates plugins for inclusion in the package

TODO: These functions will be written when it is time to create the web app portion of this.

'''
from wordfish.utils import find_directories, remove_unicode_dict, copy_directory, add_lines, wordfish_home
from glob import glob
import inspect
import json
import os
import nltk
import numpy
import pandas

def get_validation_fields():
    """
    Returns a list of tuples (each a field)
      required for a valid json
      (field,value,type)
          field: the field name
          value: indicates minimum required entires
          type: indicates the variable type

    """
    return [("name",1,str),
            ("tag",1,list),
            ("corpus",1,str), 
            ("terms",1,str),
            ("dependencies",0,dict), 
            ("arguments",0,str),
            ("contributors",0,str), 
            ("doi",0,str)]
           
def notvalid(reason):
    print(reason)
    return False


def validate(plugin_folder):
    """
    validate:
    takes a plugin folder, and looks for validation based on:

    - config.json
    - in future this will be more complex, for now just validating the config!

    """

    meta = load_plugin(plugin_folder)

    # Don't return the template folder as an option
    if meta[0]["tag"] == "template":
        return False

    if meta != None:
        if len(meta)>1:
            return notvalid("config.json has length > 1, not valid.")
        fields = get_validation_fields()
        for field,value,ftype in fields:
            if value != 0:
                # Field must exist in the keys
                if field not in meta[0].keys():
                    return notvalid("config.json is missing field %s" %(field))
                if meta[0][field] == "":
                    return notvalid("config.json must be defined for field %s" %(field))
    else:
        return notvalid("cannot load config.json")
    return True   

def get_corpus(plugins,return_field=None):
    '''get_corpus:
    return list of corpus for plugins that have it defined
    Parameters
    ==========
    plugins: dict
        list of plugins to look through (dict)
    return_file: str
        The name of a field to return, if the entire
        data structure is not desired
    Returns
    =======
    corpus: list
       list of plugins with corpus
    '''
    corpus = filter_by_field(plugins,"corpus","True")
    if return_field != None:
        corpus = [x[0][return_field] for x in corpus]
        corpus = numpy.unique(corpus).tolist()
    return corpus
    
def filter_by_field(plugins,field,field_value):
    passing = []
    for plugin in plugins:
        if plugin[0][field] == field_value:
            passing.append(plugin)
    return passing

def get_terms(plugins,return_field=None):
    '''get_terms:
    return list of corpus for plugins that have it defined
    Parameters
    ==========
    plugins: dict
        list of plugins to look through
    Returns
    =======
    terms: list
       list of plugins with terms defined
    '''
    terms = filter_by_field(plugins,"terms","True")
    if return_field != None:
        terms = [x[0][return_field] for x in terms]
        terms = numpy.unique(terms).tolist()
    return terms


def get_plugins(plugin_repo=None,load=False):
    '''get_plugins from a downloaded wordfish-plugins folder
    download plugin repo to destination folder
    Parameters
    ==========
    plugin_repo: path to plugins repo
    load: boolean
        if True, returns loaded json (dict). If false,
        returns paths to json files
    '''
    if plugin_repo == None:
        tmpdir = custom_app_download(repo_types=["plugins"])
        plugin_repo = "%s/plugins" %(tmpdir)

    plugins = find_directories(plugin_repo)
    valid_plugins = [p for p in plugins if validate(p)]
    print("Found %s valid plugins" %(len(valid_plugins)))
    if load == True:
        valid_plugins = load_plugins(valid_plugins)
    return valid_plugins


def load_plugins(plugin_folders):
    '''load_plugins:
    read in the config.json from plugin folders, return json object
    Parameters
    ==========
    plugin_folders: list
        a list of plugin folders from the wordfish-plugins repo
    Returns
    =======
    plugins:
        list of json objects, one for each plugin
    '''
    if isinstance(plugin_folders,str):
        plugin_folders = [plugin_folders]
    plugins = []
    for plugin_folder in plugin_folders:
        plugins.append(load_plugin(plugin_folder))
    return plugins

def load_plugin(plugin_folder):
    """

    load_plugin:
    reads in the config.json for an:
         
        plugin folder: full path to a plugin folder

    """
    fullpath = os.path.abspath(plugin_folder)
    config = "%s/config.json" %(fullpath)
    if not os.path.exists(config):
        return notvalid("config.json could not be found in %s" %(plugin_folder))
    try: 
        meta = json.load(open(config,"r"))
        meta = remove_unicode_dict(meta[0])
        return [meta]
    except ValueError as e:
        print("Problem reading config.json, %s" %(e))


def move_plugins(valid_plugins,app_dest):
    '''
    Moves valid plugins into the app folder for install
    
        valid_plugins: a list of full paths to valid plugin folders
        app_dest: full path to app destination folder
    '''

    moved_plugins = []
    for valid_plugin in valid_plugins:
        try:
            plugin_folder = os.path.basename(valid_plugin)
            copy_directory(valid_plugin,"%s/wordfish/plugins/%s" %(app_dest,plugin_folder))
            moved_plugins.append(valid_plugin)
        except:
           print("Cannot move %s, will not be installed." %(valid_plugin))
    return moved_plugins

# EXTRACTION JOBS ############################################################

def go_fish(tag,extraction_script):
    line_to_add = "python -c 'from wordfish.plugins.%s.functions import go_fish; go_fish()'" %(tag)
    add_lines(script=extraction_script,lines_to_add=[line_to_add])

def generate_job(func,category,inputs=None,batch_num=1):
    '''
    generate_job
    Parameters
    ==========
    func: str
        name of function to call in plugin functions.py
    category: str
        must be one of "terms" or "corpus" or "relations" corresponding to output folder
    inputs: dict
        key should be arg name, and value should be list of string args as input to func
        If inputs are not specified, it is assumed that the function will be called once
        with no inputs.
    batch_num: int
        the number of jobs to package into one job. For example, batch_num=100 will run
        func with 100 of the input items specified. Each is still written to its own
        output file.
    '''
    # Get name of calling plugin
    home = wordfish_home()
    cf = inspect.currentframe()    
    caller = inspect.getouterframes(cf, 2)
    tag = os.path.dirname(caller[1][1]).split("/")[-1]
    script = "wordfish.plugins.%s.functions" %(tag)
    output_dir = ' output_dir="%s/%s/%s"' %(home,category,tag) 

    # script name to add jobs to
    extraction_script = "%s/scripts/run_extractions_%s.job" %(home,tag)

    lines_to_add = []      
    if category in ["corpus","terms","relations"]:
        if inputs == None:
            lines_to_add.append("python -c 'from %s import %s; %s(%s)'" %(script,func,func,output_dir))
        else:
            formatted_inputs = ""
            # First collect all string args - this means same for all scripts
            for varname,elements in inputs.iteritems():
                if isinstance(elements,str):
                    single_input = format_single_input(varname,elements)
                    formatted_inputs = "%s%s" %(formatted_inputs,single_input)
                          
            # Now collect lists, must be equal length
            input_lists = dict()
            for varname,elements in inputs.iteritems():
                if isinstance(elements,list):
                    if len(input_lists)>0:
                        if len(input_lists.values()[0]) == len(elements):    
                            input_lists[varname] = elements
                    else:
                        input_lists[varname] = elements

            # If we have no input lists, just write the job with single args
            if len(input_lists) == 0:
                formatted_inputs = formatted_inputs.strip(",")
                lines_to_add.append("python -c 'from %s import %s; %s(%s,%s)'" %(script,func,func,output_dir,formatted_inputs))
            else:
                N = len(input_lists.values()[0])
                iters = int(numpy.ceil(N/float(batch_num)))
                start = 0
                for i in range(1,iters+1):
                    formatted_instance = formatted_inputs
                    if i==N:
                        end = N
                    else:
                        end = i*batch_num
                    for varname,elements in input_lists.iteritems():
                        new_input = format_inputs(varname,elements[start:end])
                        formatted_instance = "%s%s" %(formatted_instance,new_input)
                    start = end
                    formatted_instance.strip(",")
                    lines_to_add.append("python -c 'from %s import %s; %s(%s,%s)'" %(script,func,func,output_dir,formatted_instance))

        # Add lines
        add_lines(script=extraction_script,lines_to_add=lines_to_add)
    

def format_single_input(varname,element):
    if isinstance(element,str):
        element = '"%s"' %(element)
    return " %s=%s," %(varname,element) 

def format_inputs(varname,elements):
    elements = ['"%s"' %(x) if isinstance(x,str) else x for x in elements]
    return " %s=[%s]" %(varname,",".join([str(x) for x in elements])) 
