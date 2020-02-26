import requests
from bs4 import BeautifulSoup
import random
import networkx as nx
import urllib
import matplotlib.pylab as plt
import wptools
from string import ascii_uppercase

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
    data = data["query"]["pages"][list(data["query"]["pages"])[
        0]]["revisions"][0]["*"]

    # Uses BeautifulSoup html parser to remove unneeded elements
    soup = BeautifulSoup(data, "html.parser")

    # Parse the html

    table = soup.find_all("table")[0]
    tableContent = table.find_all("tbody")[0]
    for divider in tableContent.find_all('tr', class_="sortbottom"):
        divider.extract()
    tableContent.find_all('tr')[0].extract()
    for row in tableContent.find_all('tr'):
        if "<s>" in str(row):
            row.extract()
        for i, element in enumerate(row.find_all('td')):
            if i in [1, 4, 5]:
                element.extract()
            elif i == 2 and ("redlink=1" in element.find('a', href=True)["href"] or "#endnote_" in element.find('a', href=True)["href"]):
                row.extract()
            elif i == 3:
                for a in element.find_all('a'):
                    a.replaceWithChildren()
    for row in tableContent.find_all('tr'):
        elements = row.find_all('td')
        name = elements[1].find('a')
        node = urllib.parse.unquote(name["href"]).replace("/wiki/", "")
        G.add_node(node)
        G.nodes[node]["IATA"] = elements[0].contents[0]
        G.nodes[node]["Name"] = name.contents[0]
        G.nodes[node]["Location"] = "".join(
            str(item) for item in elements[2].contents)

    print("Got " + code + " IATA codes")


def parseCoords(coords):
    coords = coords.split("|")
    newCoords = list()
    for i in coords[1:]:
        newCoords.append(i)
        if i == "W" or i == "E":
            break
    coords = newCoords
    lat = dms2dd(coords[0], coords[1], coords[2], coords[3])
    lon = dms2dd(coords[4], coords[5], coords[6], coords[7])
    return (lon, lat)


def dms2dd(degs, mins, secs, dir):
    dd = float(degs) + (float(mins) / 60) + (float(secs)/3600)
    if dir == 'W' or dir == 'S':
        dd *= -1
    return dd


def getAirportInfo(airport):

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
    try:
        if index == None:
            print("Error: Airport with no destinations!")
            G.remove_node(airport)
            return -1
    except UnboundLocalError:
        print("Error: Airport with no destinations!")
        G.remove_node(airport)
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
        G.nodes[airport]["Position"] = (data["query"]["pages"][list(data["query"]["pages"])[
                                        0]]["coordinates"][0]["lon"], data["query"]["pages"][list(data["query"]["pages"])[0]]["coordinates"][0]["lat"])
    except KeyError:
        try:
            page = wptools.page(airport, silent=True).get_parse()
            G.nodes[airport]["Position"] = parseCoords(
                page.data["infobox"]["coordinates"])
        except KeyError:
            print("Error! No coordinates for this page!")
    data = data["query"]["pages"][list(data["query"]["pages"])[
        0]]["revisions"][0]["*"]
    # Uses BeautifulSoup html parser to remove unneeded elements
    soup = BeautifulSoup(data, "html.parser")
    soup.encode("utf-8")
    soup.find("div").replaceWithChildren()
    for flag in soup.find_all("span", class_="flagicon"):
        flag.extract()
    for table in soup.find_all("table", class_="stub"):
        table.extract()
    for h2 in soup.find_all("h2"):
        h2.extract()
    if "This section is empty." in str(soup):
        G.remove_node(airport)
        return -1
    try:
        if "Cargo" in soup.find().contents[0]:
            print("Error: Airport with no destinations!")
            G.remove_node(airport)
            return -1
    except AttributeError:
        print("Error: Airport with no destinations!")
        G.remove_node(airport)
        return -1
    table = soup.find("table")
    if table != None:
        if "box-More_citations_needed_section" in table["class"] or "box-Unreferenced_section" in table["class"] or "box-More_citations_needed" in table["class"]:
            table = soup.find_all("table")[1]
        table = table.find("tbody")
    else:
        print("Error: Airport with no destinations!")
        G.remove_node(airport)
        return -1

    for sup in table.find_all('sup'):
        sup.extract()
    if "<th>LOGO" in str(table):
        for row in table.find_all('tr'):
            try:
                row.find_all('td')[0].extract()
            except IndexError:
                pass
    for row in table.find_all('tr'):
        element = row.find_all('td')
        if element:
            try:
                for a in element[1].find_all('a', href=True):
                    route = tuple(
                        sorted((urllib.parse.unquote(a["href"]).replace("/wiki/", ""), airport)))
                    G.add_edge(*route)
                    if "Airlines" not in G.edges[route]:
                        G.edges[route]["Airlines"] = list()
                    if "</a>" in str(element[0]):
                        G.edges[route]["Airlines"].append(
                            element[0].find('a', href=True).contents[0])
                    else:
                        G.edges[route]["Airlines"].append(
                            element[0].contents[0])
            except IndexError:
                break

    return


def main():
    for letter in ascii_uppercase:
        getAirports(letter)
    for i, node in enumerate(list(G.nodes)):
        print(i, node)
        getAirportInfo(node)

    for node in G.nodes:
        if "Position" in G.nodes[node]:
            continue
        else:
            G.nodes[node]["Position"] = (180, 80)
    pos = nx.get_node_attributes(G, 'Position')

    nx.draw(G, pos=pos)
    labels = nx.get_node_attributes(G, 'IATA')
    nx.draw_networkx_labels(G, pos=pos, labels=labels)
    nx.write_gml(G, "Graphs/Full.gml")
    plt.show()


if __name__ == '__main__':
    main()
