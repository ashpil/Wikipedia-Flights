import networkx as nx
import requests

API = "https://en.wikipedia.org/w/api.php"
SES = requests.Session()
synonymDict = dict()


def getRedirects(pages):
    params = {
        "action": "query",
        "prop": "redirects",
        "format": "json",
        "titles": "|".join(pages),
        "rdlimit": "max",
    }
    res = SES.get(url=API, params=params)
    data = res.json()
    data = data["query"]["pages"]
    for page in data.keys():
        if "redirects" in data[page]:
            for redirect in data[page]["redirects"]:
                synonymDict[redirect["title"].replace(" ", "_")] = data[page]["title"].replace(" ", "_")


def getSynonyms(graph, verbose=False):
    pages = [node for node in graph.nodes]
    lastcount = 0
    for count in range(50, len(pages), 50):
        getRedirects(pages[lastcount:count])
        if verbose:
            print("DONE " + str(count) + "/" + str(len(pages)))
        lastcount = count
    getRedirects(pages[lastcount: lastcount + (len(pages) % 50)])
    if verbose:
        print("DONE " + str(len(pages)) + "/" + str(len(pages)))

    return synonymDict

if __name__ == '__main__':
    getSynonyms(nx.read_gml("Graphs/Full.gml"), verbose=True)
