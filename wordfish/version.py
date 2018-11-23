'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

__version__ = "1.2.0"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'wordfish'
PACKAGE_URL = "http://www.github.com/word-fish/wordfish-python"
KEYWORDS = 'wordfish, nlp, text parsing'
DESCRIPTION = "Infrastructure for finding relationships between terms in corpus of interest."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ('gensim', {'min_version': '3.6.0'}),
    ('pandas', {'min_version': '0.22.0'}),
    ('textblob', {'min_version': '0.15.1'}),
    ('nltk', {'min_version': '3.2.5'}),
    ('numpy',{'min_version': '1.14.3'}),
    ('gitpython', {'min_version': '2.1.11'}),
    ('xmltodict', {'min_version': '0.11.0'}),
    #('flask', {'min_version':'1.0.2'}),
)
