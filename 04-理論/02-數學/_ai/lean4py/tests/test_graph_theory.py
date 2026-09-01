import pytest
from lean4py.graph_theory import (
    Graph, Vertex, Edge,
    adjacency_list, adjacency_matrix,
    bfs, dfs, shortest_path, dijkstra, bellman_ford,
    is_connected, is_bipartite, connected_components, has_cycle,
    topological_sort, eulerian_path, spanning_tree, minimum_spanning_tree,
    is_complete, complement_graph
)

class TestGraphInit:
    def test_graph_empty(self):
        g = Graph()
        assert len(g.vertices) == 0

    def test_graph_vertices(self):
        g = Graph(vertices=[1, 2, 3])
        assert len(g.vertices) == 3

    def test_graph_edges(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        assert len(g.vertices) == 3

    def test_graph_weighted(self):
        g = Graph(weighted_edges=[(1, 2, 3.0), (2, 3, 4.0)])
        assert len(g.vertices) == 3
        assert g.weights[(1, 2)] == 3.0

class TestGraphOperations:
    def test_add_vertex(self):
        g = Graph()
        g.add_vertex(1)
        assert 1 in g.vertices

    def test_add_edge(self):
        g = Graph(vertices=[1, 2])
        g.add_edge(1, 2)
        assert 2 in g.neighbors(1)

    def test_remove_vertex(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        g.remove_vertex(2)
        assert 2 not in g.vertices

    def test_remove_edge(self):
        g = Graph(vertices=[1, 2], edges=[(1, 2)])
        g.remove_edge(1, 2)
        assert 2 not in g.neighbors(1)

    def test_degree(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (1, 3)])
        assert g.degree(1) == 2

class TestAdjacency:
    def test_adjacency_list(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        adj = adjacency_list(g)
        assert 1 in adj[2]
        assert 3 in adj[2]

    def test_adjacency_matrix(self):
        g = Graph(vertices=[1, 2], edges=[(1, 2)])
        vertices, matrix = adjacency_matrix(g)
        assert matrix[0][1] == 1
        assert matrix[1][0] == 1

class TestBFS:
    def test_bfs_simple(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4)])
        result = bfs(g, 1)
        assert result == [1, 2, 3, 4]

    def test_bfs_disconnected(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (3, 4)])
        result = bfs(g, 1)
        assert result == [1, 2]

class TestDFS:
    def test_dfs_simple(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4)])
        result = dfs(g, 1)
        assert result == [1, 2, 3, 4]

class TestShortestPath:
    def test_shortest_path(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4)])
        result = shortest_path(g, 1, 4)
        assert result == [1, 2, 3, 4]

    def test_shortest_path_direct(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (1, 3)])
        result = shortest_path(g, 1, 3)
        assert result == [1, 3]

class TestDijkstra:
    def test_dijkstra(self):
        g = Graph(weighted_edges=[(1, 2, 1.0), (2, 3, 2.0), (1, 3, 4.0)])
        path, dist = dijkstra(g, 1, 3)
        assert path == [1, 2, 3]
        assert abs(dist - 3.0) < 1e-10

    def test_dijkstra_no_path(self):
        g = Graph(weighted_edges=[(1, 2, 1.0)])
        result = dijkstra(g, 1, 3)
        assert result is None

class TestBellmanFord:
    def test_bellman_ford(self):
        g = Graph(weighted_edges=[(1, 2, 1.0), (2, 3, 2.0)])
        dist = bellman_ford(g, 1)
        assert dist is not None
        assert dist[1] == 0.0
        assert dist[2] == 1.0
        assert dist[3] == 3.0

class TestIsConnected:
    def test_connected(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        assert is_connected(g)

    def test_not_connected(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (3, 4)])
        assert not is_connected(g)

class TestIsBipartite:
    def test_bipartite(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 3), (2, 4)])
        assert is_bipartite(g)

    def test_not_bipartite(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (3, 1)])
        assert not is_bipartite(g)

class TestConnectedComponents:
    def test_connected_components(self):
        g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (3, 4)])
        components = connected_components(g)
        assert len(components) == 2

class TestHasCycle:
    def test_cycle(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (3, 1)])
        assert has_cycle(g)

    def test_no_cycle(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        assert not has_cycle(g)

class TestTopologicalSort:
    def test_topological_sort(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (1, 3)], directed=True)
        result = topological_sort(g)
        assert result is not None
        assert result.index(1) < result.index(2)
        assert result.index(1) < result.index(3)

class TestSpanningTree:
    def test_spanning_tree(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (1, 3)])
        tree = spanning_tree(g, 1)
        assert tree is not None
        assert len(tree.vertices) == len(g.vertices)

class TestMST:
    def test_mst(self):
        g = Graph(weighted_edges=[(1, 2, 1.0), (2, 3, 2.0), (1, 3, 5.0)])
        mst = minimum_spanning_tree(g)
        assert mst is not None
        assert len(mst.vertices) == len(g.vertices)

class TestIsComplete:
    def test_complete_graph(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3), (1, 3)])
        assert is_complete(g)

    def test_not_complete(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)])
        assert not is_complete(g)

class TestDirectedGraph:
    def test_directed_in_out_degree(self):
        g = Graph(vertices=[1, 2], edges=[(1, 2)], directed=True)
        assert g.out_degree(1) == 1
        assert g.in_degree(2) == 1

    def test_directed_bfs(self):
        g = Graph(vertices=[1, 2, 3], edges=[(1, 2), (2, 3)], directed=True)
        result = bfs(g, 1)
        assert result == [1, 2, 3]