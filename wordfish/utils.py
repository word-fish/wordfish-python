'''
utils.py
part of the wordfish python tools

'''

from urllib2 import Request, urlopen, HTTPError
from glob import glob
import errno
import tarfile
import zipfile
import urllib2
import json
import shutil
import os
import re
import __init__
import pickle

def wordfish_home():
    return os.environ["WORDFISH_HOME"]

def save_pretty_json(dict_obj,output_file):
    with open(output_file, 'w') as outfile:
        json.dump(dict_obj,outfile)

def get_installdir():
    return os.path.dirname(os.path.abspath(__init__.__file__))

def save_pkl(save_obj,pickle_file):
    pickle.dump(save_obj,open(pickle_file,"wb"))

def mkdir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return os.path.abspath(dirname)

def find_subdirectories(basepath):
    '''find_subdirectories
    Return directories (and sub) starting from a base
    '''
    directories = []
    for root, dirnames, filenames in os.walk(basepath):
        new_directories = [d for d in dirnames if d not in directories]
        directories = directories + new_directories
    return directories
    
'''
Make a directory if it doesn't exist

'''

def make_directory(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return dirname

'''
Return directories at one level specified by user
(not recursive)

'''
def find_directories(root,fullpath=True):
    directories = []
    for item in os.listdir(root):
        # Don't include hidden directories
        if not re.match("^[.]",item):
            if os.path.isdir(os.path.join(root, item)):
                if fullpath:
                    directories.append(os.path.abspath(os.path.join(root, item)))
                else:
                    directories.append(item)
    return directories

"""
remove unicode keys and values from dict, encoding in utf8

"""
def remove_unicode_dict(input_dict,encoding="utf-8"):
    output_dict = dict()
    for key,value in input_dict.iteritems():
        if isinstance(input_dict[key],list):
            output_new = [x.encode(encoding) for x in input_dict[key]]
        elif isinstance(input_dict[key],int):
            output_new = input_dict[key]
        elif isinstance(input_dict[key],float):
            output_new = input_dict[key]
        elif isinstance(input_dict[key],dict):
            output_new = remove_unicode_dict(input_dict[key])
        else:
            output_new = input_dict[key].encode(encoding)
        output_dict[key.encode(encoding)] = output_new
    return output_dict

"""
Copy an entire directory recursively

"""
 
def copy_directory(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

"""
get_template: read in and return a template file

"""
def get_template(template_file):
    filey = open(template_file,"rb")
    template = "".join(filey.readlines())
    filey.close()
    return template

"""
make a substitution for a template_tag in a template
"""
def sub_template(template,template_tag,substitution):
    template = template.replace(template_tag,substitution)
    return template

def save_template(output_file,html_snippet):
    filey = open(output_file,"w")
    filey.writelines(html_snippet)
    filey.close()

def untar(tar_file,destination="."):
    tar = tarfile.open(tar_file)
    tar.extractall(path=destination)
    tar.close()
    return tar

"""
Check type
"""
def is_type(var,types=[int,float,list]):
    for x in range(len(types)):
        if isinstance(var,types[x]):
            return True
    return False

"""
Ensure utf-8
"""
def clean_fields(mydict):
    newdict = dict()
    for field,value in mydict.iteritems():
        cleanfield = field.encode("utf-8")
        if isinstance(value,float):
            newdict[cleanfield] = value
        if isinstance(value,int):
            newdict[cleanfield] = value
        if isinstance(value,list):
            newlist = []
            for x in value:
                if not is_type(x):
                    newlist.append(x.encode("utf-8"))
                else:
                    newlist.append(x)
            newdict[cleanfield] = newlist
        else:
            newdict[cleanfield] = value.encode("utf-8")
    return newdict

# JOBS #####################################################

def add_lines(script,lines_to_add):
    if isinstance(lines_to_add,str):
        lines_to_add = [lines_to_add]
    lines = []
    if os.path.exists(script):
        filey = open(script,"rb")
        lines = [x.strip("\n") for x in filey.readlines()]
        filey.close()
    for new_line in lines_to_add:
        lines.append(new_line)
    filey = open(script,"wb")
    filey.writelines("\n".join(lines))
    filey.close()

# INTERNET ################################################
def get_url(url):
    request = Request(url)
    response = urlopen(request)
    return response.read()

def get_json(url):
    '''Return general json'''
    print url
    json_single = get_url(url)
    return json.loads(json_single.decode("utf-8"))

def read_json(json_file):
    return json.load(open(json_file,"rb"))

def has_internet_connectivity():
    """has_internet_connectivity
    Checks for internet connectivity by way of trying to
    retrieve google IP address. Returns True/False
    """
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def make_zip(path,out_zip):
    zipper = zipfile.ZipFile(out_zip, 'w')
    for root, dirs, files in os.walk(path):
        for file in files:
            zipper.write(os.path.join(root, file))
    zipper.close()
    return out_zip
