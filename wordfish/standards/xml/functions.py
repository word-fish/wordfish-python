'''
xml: general functions for parsing xml

'''

import re
import os
import tarfile
import xmltodict
from wordfish.utils import get_url

def get_xml_tree(tarball):
    '''get_xml_tree:
    get xmltree from a tarball (.tar.gz) file
    (appropriate for pubmed open content)
    Parameters
    ==========
    tarball: path (str)
        full path to .tar.gz file
    Returns
    =======
    raw: str
        raw text from the xml file
    '''
    if re.search("[.tar.gz]",tarball):
        raw = extract_xml_compressed(paper)
    else:
        raw = read_xml(tarball)
    return raw


def recursive_text_extract(xmltree,element_name):
    '''recursive_text_extract
    Return text for xml tree elements with element_name
    Parameters
    ==========
    xmltree: an xmltree object

    '''
    text = []
    queue = []
    record_ids = []
    for elem in reversed(list(xmltree)):
        queue.append(elem)

    while (len(queue) > 0):
        current = queue.pop()
        if current.text != None:
            text.append(current.text)
        if element_name in current.keys():
            record_ids.append(current.text)
        if len(list(current)) > 0:
            for elem in reversed(list(current)):
                queue.append(elem)

    return record_ids


def extract_xml_compressed(tarball):
    '''extract_xml_compressed
    Read XML from compressed file
    '''
    tar = tarfile.open(tarball, 'r:gz')
    for tar_info in tar:
        if os.path.splitext(tar_info.name)[1] == ".nxml":
            print("Extracting text from %s" %(tar_info.name))
            file_object = tar.extractfile(tar_info)
            return file_object.read().replace('\n', '')


def read_xml_url(url):
    page = get_url(url)
    return xmltodict.parse(page)
    

def read_xml(xml):
    '''read_xml
    Extract text from xml or nxml file
    Parameters
    ==========
    xml: path/str
        path to xml file
    Returns
    =======
    text with newlines replaced with ""
    '''
    with open (xml, "r") as myfile:
        return myfile.read().replace('\n', '')


def crop_text(text,remove_before="<abstract>",remove_after="<ref-list>"):
    '''crop_text
    Cut out article sections we aren't interested in
    '''
    # Remove everything before abstract
    start = re.compile(remove_before)
    end = re.compile(remove_after)
    start = start.search(text)
    end = end.search(text)
    return text[start.start():end.start()]

def remove_formatting(text,to_remove=None):
    if to_remove == None:
        to_remove = ["<italic>","<bold>","<p>","<sub>","<table>","<td>","<tr>"]
    for remove in to_remove:
        text = text.replace(remove,"")
        text = text.replace(remove.replace("<","</"),"")
    return text

def search_text(text,terms):
    '''search_text
    Search text for list of terms, return list of match counts
    '''
    vector = np.zeros(len(terms))
    for t in range(0,len(terms)):
        expression = re.compile("\s%s\s|\s%s\." %(terms[t],terms[t]))
        match = expression.findall(text)
        vector[t] = len(match)
    return vector
