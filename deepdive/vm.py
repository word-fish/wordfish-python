'''
vm: part of the deepdive python package
functions for working with virtual machines, repos

'''
from git import Repo
import tempfile
import shutil
import os


def generate_app(app_dest,app_repo=None,plugin_repo=None,plugins=None):
    '''generate 
    create an app (python module) from a template and list of plugins
    Parameters
    ==========
    app_dest: path
        folder to generate the app (python module) in
    app_repo: path
        full path to deepdive-python (template) repo
    plugins: list
        full paths to plugin folders for inclusion
    '''
    # We can only generate an in a folder that does not exist, to be safe
    if not os.path.exists(app_dest):
        if app_repo == None or plugin_repo == None:
            tmpdir = custom_app_download()
            if app_repo == None:
                app_repo = "%s/python" %(tmpdir)     
            if plugin_repo == None:
                plugin_repo = "%s/plugins" %(tmpdir)     

        # Copy app skeleton to destination
        copy_directory(app_repo,app_dest)
        valid_plugins = get_plugins(plugin_repo)

        # If the user wants to select a subset
        if plugins != None:
            subset_plugins = [x for x in valid_plugins if os.path.basename(x) in plugins]
            valid_plugins = subset_plugins  

    else:
        print "Folder exists at %s, cannot generate." %(battery_dest)



def custom_app_download(tmpdir=None,repo_types=["plugins","python"]):
    '''custom_app_download
    download both repos for the code and plugins to validate
    '''
    acceptable_types = ["plugins","python"]
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    if isinstance(repo_types,str):
        repo_types = [repo_types]
    for repo in repo_types:
        if repo in acceptable_types:
            download_repo("https://www.github.com/vsoch/deepdive-%s" %(repo),"%s/%s" %(tmpdir,repo))
        else:
            print "%s is not an acceptable option for repo_types." %(repo)
    return tmpdir


def download_repo(repo_url,tmpdir=None):
    '''download_repo
    Download a github repo to a destination
    Parameters
    ==========
    tmpdir: path
       full path to download repo to
    repo_url: path 
       full url path to repo
    destination: path
       the full path to the destination for the repo
    '''
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    Repo.clone_from(repo_url,tmpdir)
    return tmpdir


def generate_database_url(dbtype=None,username=None,password=None,host=None,table=None,template=None):
    '''
    Generate a database url from input parameters, or get a template
        dbtype: the type of database, must be one of "mysql" or "postgresql"
        username: username to connect to the database
        password: password to connect to the database
        host: database host
        table: table in the database
        template: can be one of "mysql" "sqlite3" or "postgresql" If specified, all other parameters are
                  ignored, and a default database URL is produced to work in a Vagrant VM produced by
                  psiturkpy
    
    '''
    if not template:
        if not dbtype or not username or not password or not host or not table:
            print "Please provide all inputs: dbtype,username,password,host,table."
        else:
            return "%s://%s:%s@%s/%s"  %(dbtype,
                                         username,
                                         password,
                                         host,
                                         table)
    elif template == "mysql":
        return "mysql://deepdive:deepdive@localhost:3306/deepdive"
    elif template == "postgresql":
        return "postgresql://deepdive:deepdive@localhost:5432/deepdive"


def generate_setup():
    '''
    generate_setup will generate a custom setup.py from a template
    '''
