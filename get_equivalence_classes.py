import networkx as nx
import requests
import pprint

G = nx.read_gml("Graphs/Full.gml")
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
            synonymDict[data[page]["title"]] = list()
            for redirect in data[page]["redirects"]:
                synonymDict[data[page]["title"]].append(redirect["title"])


def getSynonyms(printProgress=False):
    pages = [node for node in G.nodes]
    lastcount = 0
    for count in range(50, len(pages), 50):
        getRedirects(pages[lastcount:count])
        if printProgress:
            print("DONE " + str(count) + "/" + str(len(pages)))
        lastcount = count
    getRedirects(pages[lastcount: lastcount + (len(pages) % 50)])
    if printProgress:
        print("DONE " + str(len(pages)) + "/" + str(len(pages)))
        pp = pprint.PrettyPrinter()
        pp.pprint(synonymDict)

    return synonymDict

if __name__ == '__main__':
    getSynonyms(printProgress=True)
