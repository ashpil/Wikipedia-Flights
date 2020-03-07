
import networkx as nx
from geopy.distance import great_circle

def generateDistances(G, verbose=False):
    for edge in G.edges:
        if verbose:
            print(*edge, end=" ")
        distance = great_circle(reversed(G.nodes[edge[0]]["Position"]), reversed(G.nodes[edge[1]]["Position"])).km
        if verbose:
            print(distance)
        G.edges[edge]["Distance"] = distance

    nx.write_gml(G, "Graphs/FullFWithDistance.gml")




if __name__ == '__main__':
    generateDistances(nx.read_gml("Graphs/FullFiltered.gml"), verbose=True)
