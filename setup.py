from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application name:
    name="deepdive",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="Poldracklab + HazyResearch",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/vsoch/deepdive",

    license="LICENSE.txt",
    description="Python application for standardizing inputs, outputs, and processing steps of DeepDive for a cloud deployment/tool",
    long_description=long_description,
    keywords='deepdive, nlp, text parsing',

    install_requires = ['numpy','gitpython','nltk','neurosynth','pandas'],

    entry_points = {
        'console_scripts': [
            'ddpython=deepdive.interface:main',
        ],
    },

)
