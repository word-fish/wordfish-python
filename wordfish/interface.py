from wordfish.vm import generate_database_url, custom_app_download, generate_app
from wordfish.plugin import get_plugins, get_corpus, get_terms
from flask import Flask, render_template, request, send_file
from wordfish.utils import copy_directory, make_zip
from werkzeug import secure_filename
import webbrowser
import tempfile
import shutil
import random
import os

# WORDFISH SERVER CONFIGURATIOn #####################################
class WordfishServer(Flask):

    def __init__(self, *args, **kwargs):
            super(WordfishServer, self).__init__(*args, **kwargs)

            # download repo on start of application
            self.tmpdir = tempfile.mkdtemp()
            os.chdir(self.tmpdir)

app = WordfishServer(__name__)

"""
Get value from a form field

"""
def get_field(request,fields,value):
    if value in request.form.values():
        fields[value] = request.form[value]
    return fields

"""
Main function for starting interface to generate an application
"""
# Step 0: User is presented with base interface
@app.route('/')
def start():
    #TODO: we could define custom analysis object here 

    return render_template('index.html')

# STEP 1: Validation of user input for app
@app.route('/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            fields[field] = value
             
        # Prepare temp folder with cloned wordfish-python and wordfish-plugins
        custom_app_download(tmpdir=app.tmpdir)
    
        # Get valid plugins to present to user
        valid_plugins = get_plugins("%s/plugins/" %(app.tmpdir),load=True)
        corpus = get_corpus(valid_plugins)
        terms = get_terms(valid_plugins)
 
        return render_template('plugins.html',
                                corpus=str(corpus),
                                terms=str(terms),
                                this_many_corpus = len(corpus),
                                this_many_terms = len(terms))

    return render_template('index.html')

# STEP 2: User must select plugins to include
@app.route('/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            fields[field] = value

        # Retrieve experiment folders 
        valid_plugins = get_plugins("%s/plugins" %(app.tmpdir),load=True)
        plugins =  [x[0]["tag"] for x in valid_plugins]
        selected_plugins = [x for x in fields.values() if x in plugins]
        plugin_folders = ["%s/plugins/%s" %(app.tmpdir,x) for x in selected_plugins]

        # Add to the application
        app_dest = "%s/app" %(app.tmpdir)
        generate_app(app_dest,app_repo="%s/python"%app.tmpdir,
                              plugin_repo="%s/plugins"%app.tmpdir,
                              plugins=selected_plugins)

        # Clean up
        clean_up("%s/plugins"%(app.tmpdir))

        # Zip up application
        zipped = make_zip(app_dest,"%s/wordfish.zip" %(os.getcwd()))    

        return send_file(zipped, attachment_filename='wordfish.zip', as_attachment=True)
    return render_template('index.html')


def clean_up(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)

# Visualization functions
@app.route('/sims')
def sims():
    # For now, assume files are in running directory
    cwd = os.getcwd()
    input_files = glob("%s/*.tsv" %(cwd))
    return render_template('word2vec.html',tsv_matrices=input_files)

# This is how the command line version will run
def main(port=8088):
    if port==None:
        port=8088
    print("Let's Fish!")
    webbrowser.open("http://localhost:%s" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
