from wordfish.vm import generate_database_url, custom_app_download, generate_app
from wordfish.plugin import get_plugins, get_corpus, get_terms
from flask import Flask, render_template, request
from wordfish.utils import copy_directory
from werkzeug import secure_filename
import tempfile
import shutil
import random
import os

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','gif'])
    
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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
    tmpdir = tempfile.mkdtemp()
    return render_template('index.html',tmpdir=tmpdir)


# STEP 1: Validation of user input for app
@app.route('/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "tmpdir":
                tmpdir = value
            elif field == "dbsetupchoice":
                dbsetupchoice = value
            else:
                fields[field] = value

        # DATABASE SETUP ###################################################
        # If the user wants to generate a custom database:
        if dbsetupchoice == "manual":

            # Generate a database url from the inputs
            fields["database_url"] =  generate_database_url(dbtype=fields["dbtype"],
                                                 username=fields["dbusername"],
                                                 password=fields["dbpassword"],
                                                 host=fields["dbhost"],
                                                 table=fields["dbtable"]) 
        else:
            fields["database_url"] = generate_database_url(template="mysql")       
            
 
        # LOCAL FOLDER #####################################################
        if fields["deploychoice"] == "folder":

            # Prepare temp folder with cloned wordfish-python and wordfish-plugins
            custom_app_download(tmpdir=tmpdir)
    
        #else: TODO: vm prep here! 
            #prepare_vm(battery_dest=tmpdir,fields=fields,vm_type=fields["deploychoice"])
            #download_repo("experiments","%s/experiments/" %(tmpdir))

        # Get valid plugins to present to user
        valid_plugins = get_plugins("%s/plugins/" %(tmpdir),load=True)
        corpus = get_corpus(valid_plugins)
        terms = get_terms(valid_plugins)
 
        return render_template('plugins.html',
                                corpus=str(corpus),
                                terms=str(terms),
                                this_many_corpus = len(corpus),
                                this_many_terms = len(terms),
                                tmpdir=tmpdir,
                                deploychoice=fields["deploychoice"])

    return render_template('index.html')

# STEP 2: User must select plugins to include
@app.route('/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "tmpdir":
                tmpdir = value
            elif field == "deploychoice":
                deploychoice = value
            else:
                fields[field] = value

        # Retrieve experiment folders 
        valid_plugins = get_plugins("%s/plugins" %(tmpdir),load=True)
        plugins =  [x[0]["tag"] for x in valid_plugins]
        selected_plugins = [x for x in fields.values() if x in plugins]
        plugin_folders = ["%s/plugins/%s" %(tmpdir,x) for x in selected_plugins]

        # Option 1: A folder on the local machine
        if deploychoice == "folder":

            # Add to the application
            app_dest = "%s/app" %(tmpdir)
            generate_app(app_dest,app_repo="%s/python"%tmpdir,
                                  plugin_repo="%s/plugins"%tmpdir,
                                  plugins=selected_plugins)

        # Option 2 or 3: Virtual machine (vagrant) or cloud (aws)
        #else: #TODO:WRITEME
            #specify_experiments(battery_dest=tmpdir,experiments=selected_experiments)
            #battery_dest = tmpdir 

        # Clean up
        clean_up("%s/plugins"%(tmpdir))

        return render_template('complete.html',app_dest=app_dest)
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
def main():
    print "Let's Fish!"
    app.run(host="0.0.0.0",debug=True)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
