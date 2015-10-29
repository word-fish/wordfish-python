'''
plugin.py

part of the deepdive python package: parsing of term data structures into formats for deepdive
this set of functions finds and validates plugins for inclusion in the package

TODO: These functions will be written when it is time to create the web app portion of this.

'''
from deepdive.vm import download_repo
from deepdive.utils import find_directories, remove_unicode_dict
from glob import glob
import json
import os
import nltk
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
    print reason
    return False


def validate(plugin_folder):
    """
    validate:
    takes a plugin folder, and looks for validation based on:

    - config.json
    - in future this will be more complex, for now just validating the config!

    """

    meta = load_plugin(plugin_folder)
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


def get_plugins(plugin_repo=None,load=False):
    '''get_plugins from a downloaded deepdive-plugins folder
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
    print "Found %s valid plugins" %(len(valid_plugins))
    if load == True:
        valid_plugins = load_plugins(valid_plugins)
    return valid_plugins


def load_plugins(plugin_folders):
    '''load_plugins:
    read in the config.json from plugin folders, return json object
    Parameters
    ==========
    plugin_folders: list
        a list of plugin folders from the deepdive-plugins repo
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
        print "Problem reading config.json, %s" %(e)

