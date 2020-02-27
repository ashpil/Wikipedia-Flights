from get_equivalence_classes import getSynonyms
import networkx as nx
import matplotlib.pylab as plt

G = nx.read_gml("Graphs/Full.gml")


def main():
    synonyms = getSynonyms(G, verbose=True)
    length = len(G.nodes)
    for i, node in enumerate(list(G.nodes)):
        if node in synonyms:
            mergeNodes(synonyms[node], node)
            print(i, "/", length, "REPLACED",
                  node, "WITH", synonyms[node])

    nx.write_gml(G, "Graphs/FullFixed.gml")

# Took me soooo long to figure this out.
# This looks so much shorter without all of the print statements.
#  Issue is I thought it wasn't working when it was for a long time lmao
def mergeNodes(main, add):
    for edge in list(G.edges(add, data=True)):
        G.add_edge(*(main if connection ==
                     add else connection for connection in edge[:2]), **edge[-1])
    G.remove_node(add)


if __name__ == "__main__":
    main()
