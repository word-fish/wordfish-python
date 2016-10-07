from setuptools import setup, find_packages
import codecs
import os


setup(
    # Application name:
    name="wordfish",

    # Version number (initial):
    version="1.1.5",

    # Application author details:
    author="Poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/word-fish/wordfish-python",

    license="LICENSE.txt",
    description="Infrastructure for finding relationships between terms in corpus of interest.",
    keywords='wordfish, nlp, text parsing',

    install_requires = ["numpy","nltk","gitdb","smmap","flask","gitpython","gensim","xmltodict","pandas","textblob"],

    entry_points = {
        'console_scripts': [
            'wordfish=wordfish.interface:main',
        ],
    },

)
