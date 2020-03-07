# File: get_equivalence_classes.py

# This module creates a dictionary which holds pairs of Wikipedia page
# titles along with lists of redirect pages that link back to a given page.

import networkx as nx
import requests

API = "https://en.wikipedia.org/w/api.php"
SES = requests.Session()
SYNONYM_DICT = dict()


def getRedirects(pages):
    
    # For all page names in pages with at least one redirect, create a
    # dictionary entry in SYNONYM_DICT with a key-value pair of the page
    # title and list containing all known redirects.

    # Format: { title : [redirects], title : [redirects] }
    
    params = {
        "action": "query",
        "prop": "redirects",
        "format": "json",
        "titles": "|".join(pages),
        "rdlimit": "max",
    }

    # make GET request to API
    res = SES.get(url=API, params=params)
    # parse response
    data = res.json()
    data = data["query"]["pages"]

    for page in data.keys():
        # if a page has any redirects, add each redirect as a key
        # to SYNONYM_DICT with a value of the page.
        if "redirects" in data[page]:
            for redirect in data[page]["redirects"]:
                SYNONYM_DICT[redirect["title"].replace(" ", "_")] = data[page]["title"].replace(" ", "_")
                SYNONYM_DICT[data[page]["title"].replace(" ", "_")] = data[page]["title"].replace(" ", "_")


def getSynonyms(graph, verbose=False):
    """
    Return a dictionary of synonyms for each node in the graph
    """
    # create list containing all nodes
    pages = [node for node in graph.nodes]

    # loop through all nodes by intervals of 50
    lastcount = 0
    for count in range(50, len(pages), 50):
        # send 50 nodes to getRedirects()
        getRedirects(pages[lastcount:count])
        if verbose:
            print("DONE " + str(count) + "/" + str(len(pages)))
        # update lastcount for next cycle
        lastcount = count

    # send leftover nodes to getRedirects()
    getRedirects(pages[lastcount: lastcount + (len(pages) % 50)])

    if verbose:
        print("DONE " + str(len(pages)) + "/" + str(len(pages)))

    # return completed SYNONYM_DICT
    return SYNONYM_DICT

if __name__ == '__main__':
    getSynonyms(nx.read_gml("Graphs/Full.gml"), verbose=True)
