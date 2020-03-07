import networkx as nx

def getConnectionRundown(source, target, cityTitles=True):

    G=nx.read_gml("Graphs/FullFWithDistance.gml")


    # Get all shortest paths, pretty print them
    paths = nx.algorithms.all_shortest_paths(G, source=source, target=target)
    if cityTitles:
        paths = [[G.nodes[connection]["Location"].split(", ")[0] for connection in path] for path in paths]
    else:
        paths = [[connection.replace("_", " ") for connection in path] for path in paths]
    print(f"There are {len(paths)} routes with least layovers from {paths[0][0]} to {paths[0][-1]}:")
    for path in paths:
        print("    ", end="")
        for connection in path[0:-1]:
            print(connection, "-> ", end="")
        print(path[-1])

    print("")

    # Get path with least distance traveled, print it
    length = round(nx.shortest_path_length(G, source=source, target=target, weight="Distance"))
    paths = nx.algorithms.all_shortest_paths(G, source=source, target=target, weight="Distance")
    if cityTitles:
        path = [[G.nodes[connection]["Location"].split(", ")[0] for connection in path] for path in paths][0]
    else:
        path = [[connection.replace("_", " ") for connection in path] for path in paths][0]
    print(f"The route with least distance travelled ({length}km) is:")
    print("    ", end="")
    for connection in path[0:-1]:
        print(connection, "-> ", end="")
    print(path[-1])

def test():
    getConnectionRundown("San_Francisco_International_Airport", "Ivato_International_Airport")


if __name__ == '__main__':
    test()
