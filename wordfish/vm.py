'''
vm: part of the wordfish python package
functions for working with virtual machines, repos

'''
from wordfish.utils import copy_directory, get_template, save_template
from wordfish.plugin import get_plugins, move_plugins, load_plugins, write_plugin_relationship_job
from git import Repo
import numpy
import tempfile
import shutil
import re
import os


def generate_app(app_dest,app_repo=None,plugin_repo=None,plugins=None):
    '''generate 
    create an app (python module) from a template and list of plugins
    Parameters
    ==========
    app_dest: path
        folder to generate the app (python module) in
    app_repo: path
        full path to wordfish-python (template) repo
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

        # Generate the setup.py from template to include all python dependencies for plugins
        generate_setup(valid_plugins,app_dest)

        # Copy valid plugins into app_repo
        move_plugins(valid_plugins,app_dest)

        # Generate run commands for each of relationship extractions
        setup_relationship_extractions(valid_plugins,app_dest)

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
            download_repo("https://www.github.com/vsoch/wordfish-%s" %(repo),"%s/%s" %(tmpdir,repo))
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
                  ignored, and a default database URL is produced to work in a Vagrant VM
    
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
        return "mysql://wordfish:wordfish@localhost:3306/wordfish"
    elif template == "postgresql":
        return "postgresql://wordfish:wordfish@localhost:5432/wordfish"


def generate_setup(valid_plugins,app_dest):
    '''
    generate_setup will generate a custom setup.py from a template
    this will include the python dependencies for valid plugins
    '''
    plugin_folder = os.path.dirname(valid_plugins[0])
    v = load_plugins(valid_plugins)

    # Add plugin dependencies on other plugins, even if user has not selected
    plugin_deps = [x[0]["dependencies"]["plugins"] for x in v if "plugins" in x[0]["dependencies"]]
    for plugin_dep in plugin_deps:
        for p in plugin_dep:
            if "%s/%s" %(plugin_folder,p) not in valid_plugins:
                valid_plugins.append("%s/%s" %(plugin_folder,p))

    # Get list of python dependencies for setup.py
    python_deps = [x[0]["dependencies"]["python"] for x in v if "python" in x[0]["dependencies"]]
    dependencies = []
    for python_dep in python_deps:
        dependencies = dependencies + python_dep
    dependencies = numpy.unique(dependencies).tolist()

    # Get setup.py from app_dest to use as a template
    setup = get_template("%s/setup.py" %(app_dest)).split("\n")
    expression = re.compile("install_requires")
    startre = re.compile("[[]")
    for l in range(0,len(setup)):
        if expression.search(setup[l]):
            start = startre.search(setup[l]).start()
            old_deps = [x.strip("'").strip("'") for x in  setup[l][start:-1].strip(']').strip('[').split(",")]
            new_deps = numpy.unique(dependencies + old_deps).tolist()
            setup[l] = "%s%s" %(setup[l][0:start],str(new_deps))
    
    # Save template
    save_template("%s/setup.py" %(app_dest),"\n".join(setup))

def setup_relationship_extractions(valid_plugins,app_dest):
    '''
    setup_relationship_extractions will generate a run time script
    directory in the base of the application folder, and then, for
    each plugin for which relationship extraction is possible,
    write a line to a job script (that can be run with launch or slurm)
    to call the function.
    '''
    script_directory = "%s/scripts" %app_dest
    if not os.path.exists(script_directory):
        os.mkdir(script_directory)
    extract_relationship_script = "%s/run_extraction_relationships.job" %script_directory
    for valid_plugin in valid_plugins:
        plugin = load_plugins(valid_plugin)[0]
        if plugin[0]["relationships"] == "True":
            write_plugin_relationship_job(plugin[0]["tag"],extract_relationship_script,"%s/wordfish/scripts" %(app_dest))
