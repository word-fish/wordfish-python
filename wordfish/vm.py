'''
vm: part of the wordfish python package
functions for working with virtual machines, repos

'''
from wordfish.utils import copy_directory, get_template, save_template, get_installdir, sub_template
from wordfish.plugin import get_plugins, move_plugins, load_plugins, go_fish, load_plugin
from git import Repo
from glob import glob
import tempfile
import shutil
import numpy
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

        # Generate the requirements.txt from template to include all python dependencies for plugins
        generate_requirements(valid_plugins,app_dest)

        # Copy valid plugins into app_repo
        move_plugins(valid_plugins,app_dest)

        # Generate run commands
        setup_extraction(valid_plugins,app_dest)

    else:
        print("Folder exists at %s, cannot generate." %(battery_dest))


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
            download_repo("https://www.github.com/word-fish/wordfish-%s" %(repo),"%s/%s" %(tmpdir,repo))
        else:
            print("%s is not an acceptable option for repo_types." %(repo))
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
            print("Please provide all inputs: dbtype,username,password,host,table.")
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


def generate_requirements(valid_plugins,app_dest):
    '''
    generate_requirements will generate a custom setup.py from a template
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

    # Get requirements.txt to use as a template
    requirements = get_template("%s/requirements.txt" %(app_dest)).split("\n")
    new_requirements = numpy.unique(requirements + dependencies).tolist()
    new_requirements = [x for x in new_requirements if len(x) > 0]

    # Save new requirements
    save_template("%s/requirements.txt" %(app_dest),"\n".join(new_requirements))


def setup_extraction(valid_plugins,app_dest):
    '''
    setup_extractions will generate a run time script
    directory in the application scripts folder, and then, for
    each plugin for which some field is True,
    write a line to a job script (that can be run with launch or slurm)
    to call the function.

    '''
    script_directory = "%s/wordfish/scripts" %app_dest
    if not os.path.exists(script_directory):
        os.mkdir(script_directory)
    extraction_script = "%s/run_first.job" %(script_directory)
    for valid_plugin in valid_plugins:
        plugin = load_plugin(valid_plugin)[0]
        if plugin["corpus"] == "True" or plugin["terms"] == "True":
            go_fish(plugin["tag"],extraction_script)

def init_scripts(scripts_dir,output_base):
    '''init_scripts:
    move job running scripts from template into user
    scripts directory. Template substitutions will be done at
    this step, to ensure that calling the init_scripts function
    from a different folder will produce scripts to run with correct
    analysis directory path
    '''
    installdir = get_installdir()
    scripts_to_move = glob("%s/scripts/*" %(installdir))
    for script in scripts_to_move:
        script_template = get_template(script)
        script_name = os.path.basename(script)
        script_copy = "%s/scripts/%s" %(output_base,script_name)       
        save_template(script_copy,script_template)              
        

def make_plugin_folders(analysis_dir):
    '''
    Makes output directories for all plugins defined in the package
    for which a corpus, terms, or relationships extraction is defined.
    '''
    installdir = get_installdir()
    installed_plugins = get_plugins("%s/plugins" %(installdir),load=True)
    folders = ["corpus","terms","relations"]
    for installed_plugin in installed_plugins:
        tag = installed_plugin[0]["tag"]
        for folder in folders:
            make_plugin_folder(analysis_dir,folder,tag,installed_plugin[0][folder],"True")

def make_plugin_folder(analysis_dir,folder,tag,field_name,field_value):
    if field_name == field_value:
        plugin_folder = "%s/%s/%s" %(analysis_dir,folder,tag)
        if not os.path.exists(plugin_folder):
            os.mkdir(plugin_folder)
