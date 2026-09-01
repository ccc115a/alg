#!/usr/bin/env python3
from lean4py.graph_theory import (
    Graph, Vertex, Edge,
    adjacency_list, adjacency_matrix,
    bfs, dfs, shortest_path, dijkstra, bellman_ford,
    is_connected, is_bipartite, connected_components, has_cycle,
    topological_sort, eulerian_path, spanning_tree, minimum_spanning_tree,
    is_complete, complement_graph
)

print("=" * 60)
print("Graph Theory Module Examples")
print("=" * 60)

print("\n1. Creating a Graph:")
g = Graph(vertices=[1, 2, 3, 4, 5], edges=[(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
print(f"   Graph: {g}")
print(f"   Vertices: {g.vertices}")
print(f"   Neighbors of 1: {g.neighbors(1)}")
print(f"   Degree of 1: {g.degree(1)}")

print("\n2. Weighted Graph:")
gw = Graph(weighted_edges=[(1, 2, 3.0), (1, 3, 1.0), (2, 4, 2.0), (3, 4, 4.0), (4, 5, 1.0)])
print(f"   Weighted graph: {gw}")
print(f"   Weight of edge (1,2): {gw.weights[(1, 2)]}")
print(f"   Weight of edge (1,3): {gw.weights[(1, 3)]}")

print("\n3. BFS (Breadth-First Search):")
g = Graph(vertices=['A', 'B', 'C', 'D', 'E'], edges=[('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')])
print(f"   Graph: A-B, A-C, B-D, C-D, D-E")
print(f"   BFS from A: {bfs(g, 'A')}")
print(f"   BFS from E: {bfs(g, 'E')}")

print("\n4. DFS (Depth-First Search):")
print(f"   DFS from A: {dfs(g, 'A')}")

print("\n5. Shortest Path (Unweighted):")
path = shortest_path(g, 'A', 'E')
print(f"   Shortest path A→E: {path}")

print("\n6. Dijkstra's Algorithm (Weighted):")
gw = Graph(weighted_edges=[
    ('A', 'B', 4.0), ('A', 'C', 2.0), ('C', 'B', 1.0),
    ('C', 'D', 5.0), ('B', 'D', 1.0), ('D', 'E', 2.0)
])
path, dist = dijkstra(gw, 'A', 'E')
print(f"   Weighted graph with edges (A,B=4), (A,C=2), (C,B=1), (C,D=5), (B,D=1), (D,E=2)")
print(f"   Shortest path A→E: {path}, distance: {dist}")

print("\n7. Bellman-Ford Algorithm:")
dist = bellman_ford(gw, 'A')
print(f"   Distances from A: {dist}")

print("\n8. Connectivity:")
g1 = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
g2 = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (3, 4)])
print(f"   Graph 1 (1-2-3 connected): is_connected = {is_connected(g1)}")
print(f"   Graph 2 (two components): is_connected = {is_connected(g2)}")

print("\n9. Connected Components:")
g = Graph(vertices=[1, 2, 3, 4, 5, 6], edges=[(1, 2), (2, 3), (4, 5)])
components = connected_components(g)
print(f"   Graph with edges (1,2), (2,3), (4,5)")
print(f"   Components: {components}")

print("\n10. Bipartite Check:")
g_bip = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4)])
g_not_bip = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (3, 1)])
print(f"   Path graph (1-2-3-4): is_bipartite = {is_bipartite(g_bip)}")
print(f"   Triangle (1-2-3-1): is_bipartite = {is_bipartite(g_not_bip)}")

print("\n11. Cycle Detection:")
g_cycle = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4), (4, 1)])
g_no_cycle = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4)])
print(f"   Square (1-2-3-4-1): has_cycle = {has_cycle(g_cycle)}")
print(f"   Path (1-2-3-4): has_cycle = {has_cycle(g_no_cycle)}")

print("\n12. Topological Sort (DAG):")
g_dag = Graph(vertices=['A', 'B', 'C', 'D'], edges=[('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')], directed=True)
topo = topological_sort(g_dag)
print(f"   DAG: A→B, A→C, B→D, C→D")
print(f"   Topological order: {topo}")

print("\n13. Spanning Tree:")
g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4), (1, 4)])
tree = spanning_tree(g, 1)
print(f"   Complete graph minus one edge")
print(f"   Spanning tree edges: {list(tree.weights.keys())}")

print("\n14. Minimum Spanning Tree:")
gw = Graph(weighted_edges=[
    (1, 2, 1.0), (1, 3, 4.0), (2, 3, 2.0), (2, 4, 5.0), (3, 4, 3.0)
])
mst = minimum_spanning_tree(gw)
print(f"   Weighted graph with 5 edges")
print(f"   MST edges: {list(mst.weights.keys())}")

print("\n15. Complete Graph Check:")
g_complete = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (1, 3)])
g_incomplete = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
print(f"   Triangle: is_complete = {is_complete(g_complete)}")
print(f"   Path (1-2-3): is_complete = {is_complete(g_incomplete)}")

print("\n16. Directed Graph:")
g_dir = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)], directed=True)
print(f"   Directed graph: 1→2→3")
print(f"   out_degree(1) = {g_dir.out_degree(1)}")
print(f"   in_degree(3) = {g_dir.in_degree(3)}")

print("\n17. Add/Remove Operations:")
g = Graph(vertices=[1, 2], edges=[(1, 2)])
g.add_vertex(3)
g.add_edge(2, 3)
print(f"   After adding vertex 3 and edge (2,3): {g.vertices}")
g.remove_edge(1, 2)
print(f"   After removing edge (1,2): {list(g.adjacency[1])}")
g.remove_vertex(1)
print(f"   After removing vertex 1: {g.vertices}")

print("\n18. Adjacency Representations:")
g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
adj = adjacency_list(g)
print(f"   Adjacency list: {adj}")
vertices, matrix = adjacency_matrix(g)
print(f"   Adjacency matrix vertices: {vertices}")
print(f"   Adjacency matrix: {matrix}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)