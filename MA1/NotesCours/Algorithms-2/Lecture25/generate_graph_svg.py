import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import scipy

def hexagonal_lattice_with_hole():
    #graph = nx.generators.lattice.hexagonal_lattice_graph(20, 20)
    #for u in range(9, 12):
    #    for v in range(19, 22):
    #        graph.remove_node((u, v))
    graph = nx.generators.lattice.hexagonal_lattice_graph(40, 40)
    for u in range(18, 23):
        for v in range(35, 46):
            graph.remove_node((u, v))
    return graph

def grid_pos(graph):
    return nx.get_node_attributes(graph, 'pos')

def custom_spectral_pos(graph, use_smallest):
    laplacian_matrix = nx.laplacian_matrix(graph).toarray()
    _, eigenvectors = scipy.linalg.eigh(laplacian_matrix)
    if use_smallest: 
        eigenvec_x = eigenvectors[:, 1]
        eigenvec_y = eigenvectors[:, 2]
    else:
        eigenvec_x = eigenvectors[:, -2]
        eigenvec_y = eigenvectors[:, -1]

    return {node: (eigenvec_x[i], eigenvec_y[i]) for i, node in enumerate(graph.nodes)}


matplotlib.use('svg')
graph = hexagonal_lattice_with_hole()
    
for pos, name in [
    (grid_pos(graph), "HexagonalLatticeWithHole_Grid.svg"),
    (custom_spectral_pos(graph, True), "HexagonalLatticeWithHole_SmallEigs.svg"),
    (custom_spectral_pos(graph, False), "HexagonalLatticeWithHole_LargeEigs.svg"),
]:
    plt.figure(figsize=(8, 8))
    nx.draw(graph, pos=pos, edge_color="k", with_labels=False, node_size=0)
    plt.savefig(name, format="svg")
    #plt.savefig(name, dpi=200)
