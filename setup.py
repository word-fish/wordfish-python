from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application name:
    name="wordfish",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="Poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/vsoch/wordfish-python",

    license="LICENSE.txt",
    description="Infrastructure for finding relationships between terms in corpus of interest.",
    long_description=long_description,
    keywords='wordfish, nlp, text parsing',

    install_requires = ['numpy','gitpython','nltk','pandas'],

    entry_points = {
        'console_scripts': [
            'wordfish=wordfish.interface:main',
        ],
    },

)
