import requests
from bs4 import BeautifulSoup
import random

API = "https://en.wikipedia.org/w/api.php"
SES = requests.Session()

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
        airports = list()
        for row in tableContent.find_all('tr'):
            elements = row.find_all('td')
            dic = dict()
            dic["IATA"] = elements[0].contents[0]
            name = elements[1].find_all('a')[0]
            dic["Link"] = name["href"]
            dic["Name"] = name.contents[0]
            dic["Location"] = "".join(str(item) for item in elements[2].contents)
            airports.append(dic)

        

        return airports

def getAirportInfo(airport):

        params = {
            "action": "parse",
            "prop": "sections",
            "format": "json",
            "page": airport,
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
            return "Error! " + airport

        params = {
            "action": "query",
            "prop": "revisions",
            "format": "json",
            "titles": airport,
            "rvprop": "content",
            "rvparse": True,
            "rvlimit": 1,
            "rvsection": index
        }

        res = SES.get(url=API, params=params)
        data = res.json()
        data = data["query"]["pages"][list(data["query"]["pages"])[0]]["revisions"][0]["*"]

        # Uses BeautifulSoup html parser to remove unneeded elements
        soup = BeautifulSoup(data, "html.parser")

        table = soup.find("table").find("tbody")

        for sup in table.find_all('sup'):
            sup.extract()

        connections = set()
        attributes = dict()
        for row in table.find_all('tr'):
            element = row.find_all('td')
            if element:
                for a in element[1].find_all('a', href=True):
                    route = tuple(sorted((a["href"], "/wiki/" + airport)))
                    connections.add(route)
                    attributes[route] = dict()
                    if "Airlines" not in attributes[route]:
                        attributes[route]["Airlines"] = list()
                    attributes[route]["Airlines"].append(element[0].find('a', href=True).contents[0])


        
        
            

if __name__ == '__main__':
    getAirportInfo("Samaná_El_Catey_International_Airport")
