import networkx as nx
import matplotlib.pylab as plt

def main(G=nx.read_gml("Graphs/FullFiltered.gml")):
    pos = nx.get_node_attributes(G, 'Position')
    nx.draw(G, pos=pos)
    labels = nx.get_node_attributes(G, 'IATA')
    nx.draw_networkx_labels(G, pos=pos, labels=labels)
    plt.show()


if __name__ == "__main__":
    main()