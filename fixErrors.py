from get_equivalence_classes import getSynonyms
import networkx as nx
import matplotlib.pylab as plt
import wptools

def removeNonValidAirports(G, verbose=False):
    for i, node in enumerate(list(G.nodes(data=True))):
        if "IATA" not in node[1]:
            if verbose:
                print(i, node[0], len(G.edges(node[0])), end=" ")
            try:
                page = wptools.page(node[0], silent=True).get_parse()
                iata = page.data["infobox"]["IATA"]
                if verbose:
                    print(iata, end=" ")
                if "none" in iata.lower() or "pending" in iata.lower() or "n/a" in iata.lower() or "<s>" in iata.lower():
                    raise TypeError
            except (LookupError, TypeError) as e:
                if verbose:
                    print("\033[31mNOT VALID PAGE/NO IATA CODE!\033[0m", end="")
                G.remove_node(node[0])
            if verbose:
                print()


def findAirpotsWithNoDestinations(G, verbose=False):
    count = 0
    for i, node in enumerate(list(G.nodes)):
        if len(G.edges(node)) == 0:
            if verbose:
                print(i, node)
            count += 1
            G.remove_node(node)
    if verbose:
        print("\033[31mTOTAL:", count, "\033[0m")

def removeHeliports(G, verbose=False):
    count = 0
    for i, node in enumerate(list(G.nodes)):
        if "heliport" in node.lower():
            if verbose:
                print("REMOVED", i, node)
            G.remove_node(node)
            count += 1
    if verbose:
        print("\033[31mREMOVED", count, "HELIPORTS\033[0m")

def main(G=nx.read_gml("Graphs/FullNoRedirects2.gml")):
    findAirpotsWithNoDestinations(G, True)
    removeHeliports(G, True)
    removeNonValidAirports(G, True)

    # Draw it. Prettyyyy
    pos = nx.get_node_attributes(G, 'Position')
    nx.draw(G, pos=pos)
    labels = nx.get_node_attributes(G, 'IATA')
    nx.draw_networkx_labels(G, pos=pos, labels=labels)
    nx.write_gml(G, "Graphs/FullNoRedirectsRemovedWrong&Heliports&NoDest.gml")
    plt.show()

if __name__ == "__main__":
    main()
