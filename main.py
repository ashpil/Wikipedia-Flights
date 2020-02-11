import requests
from bs4 import BeautifulSoup
import random
import networkx as nx

API = "https://en.wikipedia.org/w/api.php"
SES = requests.Session()
G = nx.Graph()

def getAirports(code):
        params = {
            "action": "query",
            "prop": "revisions",
            "format": "json",
            "titles": "List of airports by IATA code: " + code,
            "rvprop": "content",
            "rvparse": True,
            "rvlimit": 1
        }


        res = SES.get(url=API, params=params)
        data = res.json()
        data = data["query"]["pages"][list(data["query"]["pages"])[0]]["revisions"][0]["*"]

        # Uses BeautifulSoup html parser to remove unneeded elements
        soup = BeautifulSoup(data, "html.parser")

        # Parse the html

        table = soup.find_all("table")[0]
        tableContent = table.find_all("tbody")[0]
        for divider in tableContent.find_all('tr', class_="sortbottom"):
            divider.extract()
        tableContent.find_all('tr')[0].extract()
        for row in tableContent.find_all('tr'):
            for i, element in enumerate(row.find_all('td')):
                if i in [1,4,5]:
                    element.extract()
                elif i == 2 and "redlink=1" in element.find_all('a', href=True)[0]["href"]:
                    row.extract()
                elif i == 3:
                    for a in element.find_all('a'):
                        a.replaceWithChildren()
        for row in tableContent.find_all('tr'):
            elements = row.find_all('td')
            name = elements[1].find_all('a')[0]
            G.add_node(name["href"])
            G.nodes[name["href"]]["IATA"] = elements[0].contents[0]
            G.nodes[name["href"]]["Name"] = name.contents[0]
            G.nodes[name["href"]]["Location"] = "".join(str(item) for item in elements[2].contents)

        

def getAirportInfo(airport, nodeName):

        airport = airport.replace(" ", "_")
        params = {
            "action": "parse",
            "prop": "sections",
            "format": "json",
            "page": airport,
            "redirects": 1
        }


        res = SES.get(url=API, params=params)
        data = res.json()
        for section in data["parse"]["sections"]:
            if section["anchor"] == "Airlines_and_destinations":
                index = section["index"]
                break
            else:
                index = None
        
        if index == None:
            print("Error: Airport with no destinations!")
            G.remove_node(nodeName)
            return -1

        params = {
            "action": "query",
            "prop": "revisions|coordinates",
            "format": "json",
            "titles": airport,
            "rvprop": "content",
            "rvparse": True,
            "rvlimit": 1,
            "rvsection": index,
            "redirects": 1
        }

        res = SES.get(url=API, params=params)
        data = res.json()
        try:
            G.nodes[nodeName]["lon"] = data["query"]["pages"][list(data["query"]["pages"])[0]]["coordinates"][0]["lon"]
            G.nodes[nodeName]["lat"] = data["query"]["pages"][list(data["query"]["pages"])[0]]["coordinates"][0]["lat"]
        except KeyError:
            G.nodes[nodeName]["lon"] = "assign manually!"
            G.nodes[nodeName]["lat"] = "assign manually!"
        data = data["query"]["pages"][list(data["query"]["pages"])[0]]["revisions"][0]["*"]

        # Uses BeautifulSoup html parser to remove unneeded elements
        soup = BeautifulSoup(data, "html.parser")

        soup.find("div").replaceWithChildren()
        for h2 in soup.find_all("h2"):
            h2.extract()
        if "Cargo" in soup.find().contents[0]:
            print("Error: Airport with no destinations!")
            G.remove_node(nodeName)
            return -1
        table = soup.find("table")
        if table != None:
            table = table.find("tbody")
        else:
            print("Error: Airport with no destinations!")
            G.remove_node(nodeName)
            return -1

        for sup in table.find_all('sup'):
            sup.extract()

        for row in table.find_all('tr'):
            element = row.find_all('td')
            if element:
                for a in element[1].find_all('a', href=True):
                    route = tuple(sorted((fixTitle(a["href"]), "/wiki/" + airport)))
                    G.add_edge(*route)
                    if "Airlines" not in G.edges[route]:
                        G.edges[route]["Airlines"] = list()
                    G.edges[route]["Airlines"].append(element[0].find('a', href=True).contents[0])
        
        return


def fixTitle(title):
    fixes = {
        "_%E2%80%93_": "–",
        "%C3%A9": "é",
    }
    
    for fix in list(fixes):
        title = title.replace(fix, fixes[fix])

    return title


def main():
    getAirports("A")
    for i, node in enumerate(list(G.nodes)):
        if i < 87:
            continue
        print(i, G.nodes[node]["Name"])
        getAirportInfo(G.nodes[node]["Name"], node)
        if i == 100:
            break
    print("----EDGES----")
    for edge in G.edges:
        print(edge)

if __name__ == '__main__':
    main()
