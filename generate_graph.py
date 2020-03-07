import requests
import urllib
import wptools
import time
import datetime
import networkx as nx
import matplotlib.pylab as plt
from bs4 import BeautifulSoup
from string import ascii_uppercase
from get_equivalence_classes import getSynonyms

API = "https://en.wikipedia.org/w/api.php"
SES = requests.Session()
SYNONYM_DICT = dict()


# Code to parse IATA page tables and put those into graph as nodes with attributes
def getAirports(G, code):
    params = {
        "action": "query",
        "prop": "revisions",
        "format": "json",
        "titles": "List of airports by IATA code: " + code,
        "rvprop": "content",
        "rvparse": True,
        "rvlimit": 1
    }

    data = SES.get(url=API, params=params).json()
    data = list(data["query"]["pages"].values())[0]["revisions"][0]["*"]

    # Uses BeautifulSoup html parser to remove unneeded elements/parse HTML
    soup = BeautifulSoup(data, "html.parser")
    tableContent = soup.find("table").find("tbody")

    # Strip extra stuff from table that gets in the way
    for divider in tableContent.find_all('tr', class_="sortbottom"):
        divider.extract()
    tableContent.find('tr').extract()

    # Format each table element to be easier to parse
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

    # Go through table, adding each entry to our graph
    for row in tableContent.find_all('tr'):
        elements = row.find_all('td')
        name = elements[1].find('a')
        node = urllib.parse.unquote(getRedirect(
            name["href"].replace("/wiki/", "")))
        G.add_node(node)
        G.nodes[node]["IATA"] = elements[0].contents[0]
        G.nodes[node]["Name"] = name.contents[0]
        G.nodes[node]["Location"] = "".join(
            str(item) for item in elements[2].contents)


# Gets info for given airport and populates its nodes attributes and edges
def getAirportInfo(G, airport):
    # Basically this is tons of if statements to check for certain exceptions
    # and do proper thing if they occur. There's likely a better way to do this

    # Get section of routes
    params = {
        "action": "parse",
        "prop": "sections",
        "format": "json",
        "page": airport,
        "redirects": 1
    }

    data = SES.get(url=API, params=params).json()

    index = 0
    for section in data["parse"]["sections"]:
        if section["anchor"] == "Airlines_and_destinations":
            index = section["index"]
            break

    # Get coordinates and routes
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

    data = SES.get(url=API, params=params).json()
    data = list(data["query"]["pages"].values())[0]
    # All coord stuff happens here
    try:
        G.nodes[airport]["Position"] = (data["coordinates"][0]["lon"], data["coordinates"][0]["lat"])
    except KeyError:
        try:
            page = wptools.page(airport, silent=True).get_parse()
            G.nodes[airport]["Position"] = parseCoords(
                page.data["infobox"]["coordinates"])
        except (KeyError, TypeError):
            G.nodes[airport]["Position"] = (180, 80)

    if index == 0:
        return

    # Uses BeautifulSoup html parser to remove unneeded elements
    data = data["revisions"][0]["*"]
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
        return -1
    try:
        if "Cargo" in soup.find().contents[0]:
            return -1
    except AttributeError:
        return -1
    table = soup.find("table")
    if table != None:
        if "box-More_citations_needed_section" in table["class"] or "box-Unreferenced_section" in table["class"] or "box-More_citations_needed" in table["class"]:
            table = soup.find_all("table")[1]
        table = table.find("tbody")
    else:
        return -1

    for sup in table.find_all('sup'):
        sup.extract()
    if "<th>LOGO" in str(table):
        for row in table.find_all('tr'):
            try:
                row.find_all('td')[0].extract()
            except IndexError:
                pass

    # Add cleaned up data to node
    for row in table.find_all('tr'):
        element = row.find_all('td')
        if element:
            try:
                for a in element[1].find_all('a', href=True):
                    route = tuple((urllib.parse.unquote(getRedirect(
                        a["href"].replace("/wiki/", ""))), airport))
                    G.add_edge(*route)
                    if "Airlines" not in G.edges[route]:
                        G.edges[route]["Airlines"] = list()
                    if "</a>" in str(element[0]):
                        if element[0].find('a', href=True).contents[0] not in G.edges[route]["Airlines"]:
                            G.edges[route]["Airlines"].append(
                                element[0].find('a', href=True).contents[0])
                    elif element[0].contents[0] not in G.edges[route]["Airlines"]:
                        G.edges[route]["Airlines"].append(
                            element[0].contents[0])
            except IndexError:
                break

    return


# Coords DMS -> DD
def parseCoords(coords):
    coords = coords.split("|")
    newCoords = list()
    for i in coords[1:]:
        newCoords.append(i)
        if i == "W" or i == "E":
            break
    coords = newCoords
    try:
        lat = dms2dd(coords[0], coords[1], coords[2], coords[3])
        lon = dms2dd(coords[4], coords[5], coords[6], coords[7])
    except IndexError:
        lat = dms2dd(coords[0], 0, "bad", "bad")
        lon = dms2dd(coords[1], 0, "bad", "bad")
    return (lon, lat)


def dms2dd(degs, mins, secs, dir):
    try:
        dd = float(degs) + (float(mins) / 60) + (float(secs)/3600)
        if dir == 'W' or dir == 'S':
            dd *= -1
    except ValueError:
        print("PAGE USING DEPRICATED COORD SYSTEM")
        try:
            dd = float(degs) + (float(mins) / 60)
            if (secs == 'W' or secs == 'S'):
                dd *= -1
        except ValueError:
            dd = float(degs)
            if (mins == 'W' or mins == 'S'):
                dd *= -1
    return dd


# Gets redirect if not in dict, stores known ones in dict to decrease request calls
def getRedirect(link):
    if link in SYNONYM_DICT:
        return SYNONYM_DICT[link]
    else:
        r = requests.get("https://en.wikipedia.org/wiki/" + link)
        soup = BeautifulSoup(r.content, "html.parser")
        newLink = soup.find("link", {"rel": "canonical"})
        airport = newLink["href"].split("/wiki/")[-1]
        SYNONYM_DICT[link] = airport
        return airport


def generateGraph(name, verbose=False):
    G = nx.Graph()

    # Populate graph from IATA page
    if verbose:
        start = time.time()
    for letter in ascii_uppercase[0:1]:
        if verbose:
            letterTime = time.time()
        getAirports(G, letter)
        if verbose:
            print("GOT", letter, "IATA CODES IN", datetime.timedelta(
            seconds=time.time() - letterTime))
    if verbose:
        print("GOT ALL CODES IN", datetime.timedelta(seconds=time.time() - start))

    # Gets redirects all at once to speed things up
    if verbose:
        timeTemp = time.time()
    SYNONYM_DICT.update(getSynonyms(G, verbose=verbose))
    if verbose:
        print("GOT SYNONYMS IN", datetime.timedelta(seconds=time.time() - timeTemp))

    # Get data for each node from its page
    if verbose:
        timeTemp = time.time()
    for i, node in enumerate(list(G.nodes)):
        if verbose:
            print(i, node)
        getAirportInfo(G, node)
    if verbose:
        print("GOT AIRPORTS/CONNECTIONS IN",
          datetime.timedelta(seconds=time.time() - timeTemp))

    nx.write_gml(G, "Graphs/" + name + ".gml")
    if verbose:
        print("FULL TIME ELAPSED:", datetime.timedelta(seconds=time.time() - start))
        print("DONE")


if __name__ == '__main__':
    generateGraph("Full", verbose=True)
