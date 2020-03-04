from get_equivalence_classes import getSynonyms
import networkx as nx
import matplotlib.pylab as plt
import wptools

G = nx.read_gml("Graphs/FullNoRedirects2.gml")

def removeNonValidAirports():
    for i, node in enumerate(list(G.nodes(data=True))):
        if "IATA" not in node[1]:
            print(i, node[0], len(G.edges(node[0])), end=" ")
            try:
                page = wptools.page(node[0], silent=True).get_parse()
                iata = page.data["infobox"]["IATA"]
                print(iata, end=" ")
                if iata == "none" or iata == "pending":
                    raise TypeError
            except (LookupError, TypeError) as e:
                print("\033[31mNOT VALID PAGE/NO IATA CODE!\033[0m", end="")
                G.remove_node(node[0])
            print()

    # Draw it. Prettyyyy
    pos = nx.get_node_attributes(G, 'Position')
    nx.draw(G, pos=pos)
    labels = nx.get_node_attributes(G, 'IATA')
    nx.draw_networkx_labels(G, pos=pos, labels=labels)
    nx.write_gml(G, "Graphs/FullNoRedirectsFixedSomeErrors.gml")
    plt.show()

def findAirpotsWithNoDestinations():
    count = 0
    for i, node in enumerate(list(G.nodes)):
        if len(G.edges(node)) == 0:
            print(i, node)
            count += 1
            G.remove_node(node)
    print("TOTAL:", count)

    # Draw it. Prettyyyy
    pos = nx.get_node_attributes(G, 'Position')
    nx.draw(G, pos=pos)
    labels = nx.get_node_attributes(G, 'IATA')
    nx.draw_networkx_labels(G, pos=pos, labels=labels)
    nx.write_gml(G, "Graphs/FullNoRedirectsFixedSomeErrorsRemovedNoDestinations.gml")
    plt.show()
    
if __name__ == "__main__":
    findAirpotsWithNoDestinations()
