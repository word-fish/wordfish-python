'''
vm: part of the deepdive python package
functions for working with virtual machines, repos

'''
from git import Repo
import tempfile
import shutil
import os

def download_repo(repo_url,destination):
    '''download_repo
    Download a github repo to a destination
    Parameters
    ==========
    repo_url: path 
       full url path to repo
    destination: path
       the full path to the destination for the repo
    '''
    return Repo.clone_from(repo_url, destination)


def tmp_download(tmpdir=None,repo_url):
    '''tmp_download
    download a repo to a temporary folder, return path to repo in temp directory
    tmpdir: path 
        The directory to download to. If none, a temporary directory will be made
    repo_url: url
        The repository to download
    '''
    if not tmpdir:
        tmpdir = tempfile.mkdtemp()
    download_repo(repo_url,tmpdir)
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
