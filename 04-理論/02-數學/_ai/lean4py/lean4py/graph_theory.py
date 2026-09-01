from typing import Dict, List, Optional, Set, Tuple, Callable, Any
from collections import deque
import heapq

class Vertex:
    def __init__(self, id: Any, data: Optional[Any] = None):
        self.id = id
        self.data = data

    def __repr__(self):
        return f"Vertex({self.id})"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

class Edge:
    def __init__(self, u: Any, v: Any, weight: float = 1.0):
        self.u = u
        self.v = v
        self.weight = weight

    def __repr__(self):
        if self.weight != 1.0:
            return f"Edge({self.u} --({self.weight})--> {self.v})"
        return f"Edge({self.u} -> {self.v})"

    def __eq__(self, other):
        return self.u == other.u and self.v == other.v

    def __hash__(self):
        return hash((self.u, self.v))

class Graph:
    def __init__(self, vertices: Optional[List[Any]] = None, edges: Optional[List[Tuple[Any, Any]]] = None,
                 weighted_edges: Optional[List[Tuple[Any, Any, float]]] = None, directed: bool = False):
        self.vertices = set(vertices) if vertices else set()
        self.directed = directed
        self.adjacency: Dict[Any, Set[Any]] = {v: set() for v in self.vertices}
        self.weights: Dict[Tuple[Any, Any], float] = {}

        edge_list = edges or []
        for u, v in edge_list:
            self.add_edge(u, v)

        if weighted_edges:
            for u, v, w in weighted_edges:
                self.add_edge(u, v, w)

    def __repr__(self):
        return f"Graph(V={len(self.vertices)}, E={len(self.adjacency) if not self.directed else sum(len(v) for v in self.adjacency.values())})"

    def add_vertex(self, v: Any) -> None:
        self.vertices.add(v)
        if v not in self.adjacency:
            self.adjacency[v] = set()

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].add(v)
        self.weights[(u, v)] = weight
        if not self.directed:
            self.adjacency[v].add(u)
            self.weights[(v, u)] = weight

    def remove_vertex(self, v: Any) -> None:
        if v in self.vertices:
            self.vertices.remove(v)
            for u in list(self.adjacency.get(v, set())):
                self.adjacency[u].discard(v)
                self.weights.pop((u, v), None)
            self.adjacency.pop(v, None)
            self.weights = {k: w for k, w in self.weights.items() if v not in k}

    def remove_edge(self, u: Any, v: Any) -> None:
        if u in self.adjacency:
            self.adjacency[u].discard(v)
        if not self.directed and v in self.adjacency:
            self.adjacency[v].discard(u)
        self.weights.pop((u, v), None)
        if not self.directed:
            self.weights.pop((v, u), None)

    def neighbors(self, v: Any) -> Set[Any]:
        return self.adjacency.get(v, set())

    def degree(self, v: Any) -> int:
        return len(self.adjacency.get(v, set()))

    def in_degree(self, v: Any) -> int:
        if not self.directed:
            return self.degree(v)
        count = 0
        for u in self.vertices:
            if v in self.adjacency.get(u, set()):
                count += 1
        return count

    def out_degree(self, v: Any) -> int:
        if not self.directed:
            return self.degree(v)
        return self.degree(v)

def adjacency_list(g: Graph) -> Dict[Any, List[Any]]:
    return {v: list(g.neighbors(v)) for v in g.vertices}

def adjacency_matrix(g: Graph) -> Tuple[List[Any], List[List[int]]]:
    vertices = list(g.vertices)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    matrix = [[0] * n for _ in range(n)]
    for u in g.vertices:
        for v in g.neighbors(u):
            matrix[idx[u]][idx[v]] = 1
    return vertices, matrix

def bfs(g: Graph, start: Any) -> List[Any]:
    visited = set()
    queue = deque([start])
    result = []

    while queue:
        v = queue.popleft()
        if v not in visited:
            visited.add(v)
            result.append(v)
            for neighbor in g.neighbors(v):
                if neighbor not in visited:
                    queue.append(neighbor)

    return result

def dfs(g: Graph, start: Any) -> List[Any]:
    visited = set()
    result = []

    def dfs_rec(v):
        visited.add(v)
        result.append(v)
        for neighbor in g.neighbors(v):
            if neighbor not in visited:
                dfs_rec(neighbor)

    dfs_rec(start)
    return result

def dfs_iterative(g: Graph, start: Any) -> List[Any]:
    visited = set()
    stack = [start]
    result = []

    while stack:
        v = stack.pop()
        if v not in visited:
            visited.add(v)
            result.append(v)
            for neighbor in g.neighbors(v):
                if neighbor not in visited:
                    stack.append(neighbor)

    return result

def shortest_path(g: Graph, start: Any, end: Any) -> Optional[List[Any]]:
    if start not in g.vertices or end not in g.vertices:
        return None

    visited = set()
    queue = deque([(start, [start])])

    while queue:
        v, path = queue.popleft()
        if v == end:
            return path
        if v in visited:
            continue
        visited.add(v)
        for neighbor in g.neighbors(v):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None

def dijkstra(g: Graph, start: Any, end: Any) -> Optional[Tuple[List[Any], float]]:
    if start not in g.vertices or end not in g.vertices:
        return None

    distances = {v: float('inf') for v in g.vertices}
    distances[start] = 0
    previous = {v: None for v in g.vertices}
    pq = [(0, start)]
    visited = set()

    while pq:
        dist, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)

        if v == end:
            break

        for neighbor in g.neighbors(v):
            weight = g.weights.get((v, neighbor), 1.0)
            alt = dist + weight
            if alt < distances[neighbor]:
                distances[neighbor] = alt
                previous[neighbor] = v
                heapq.heappush(pq, (alt, neighbor))

    if distances[end] == float('inf'):
        return None

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return path, distances[end]

def bellman_ford(g: Graph, start: Any) -> Optional[Dict[Any, float]]:
    if start not in g.vertices:
        return None

    distances = {v: float('inf') for v in g.vertices}
    distances[start] = 0

    for _ in range(len(g.vertices) - 1):
        for u in g.vertices:
            for v in g.neighbors(u):
                weight = g.weights.get((u, v), 1.0)
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight

    for u in g.vertices:
        for v in g.neighbors(u):
            weight = g.weights.get((u, v), 1.0)
            if distances[u] + weight < distances[v]:
                return None

    return distances

def is_connected(g: Graph) -> bool:
    if not g.vertices:
        return True
    if not g.directed:
        start = next(iter(g.vertices))
        visited = set()
        stack = [start]
        while stack:
            v = stack.pop()
            if v not in visited:
                visited.add(v)
                stack.extend(g.neighbors(v) - visited)
        return len(visited) == len(g.vertices)
    else:
        for v in g.vertices:
            visited = set()
            stack = [v]
            while stack:
                u = stack.pop()
                if u not in visited:
                    visited.add(u)
                    stack.extend(g.neighbors(u) - visited)
            if len(visited) != len(g.vertices):
                return False
        return True

def is_bipartite(g: Graph) -> bool:
    if not g.vertices:
        return True
    color = {}
    queue = deque([next(iter(g.vertices))])
    color[queue[0]] = 0

    while queue:
        v = queue.popleft()
        for neighbor in g.neighbors(v):
            if neighbor not in color:
                color[neighbor] = 1 - color[v]
                queue.append(neighbor)
            elif color[neighbor] == color[v]:
                return False
    return True

def connected_components(g: Graph) -> List[List[Any]]:
    visited = set()
    components = []

    for start in g.vertices:
        if start in visited:
            continue
        component = bfs(g, start)
        components.append(component)
        visited.update(component)

    return components

def has_cycle(g: Graph) -> bool:
    visited = set()
    rec_stack = set()

    def dfs_cycle(v, parent=None):
        visited.add(v)
        rec_stack.add(v)
        for neighbor in g.neighbors(v):
            if neighbor not in visited:
                if dfs_cycle(neighbor, v):
                    return True
            elif neighbor in rec_stack and neighbor != parent:
                return True
        rec_stack.remove(v)
        return False

    for v in g.vertices:
        if v not in visited:
            if dfs_cycle(v):
                return True
    return False

def topological_sort(g: Graph) -> Optional[List[Any]]:
    if g.directed:
        in_degree = {v: g.in_degree(v) for v in g.vertices}
        queue = deque([v for v in g.vertices if in_degree[v] == 0])
        result = []

        while queue:
            v = queue.popleft()
            result.append(v)
            for neighbor in g.neighbors(v):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(g.vertices):
            return None
        return result
    return None

def eulerian_path(g: Graph) -> Optional[List[Any]]:
    if has_cycle(g):
        return None

    odd_degree = [v for v in g.vertices if g.degree(v) % 2 == 1]
    if len(odd_degree) not in [0, 2]:
        return None

    start = odd_degree[0] if odd_degree else next(iter(g.vertices))
    stack = [start]
    path = []
    temp_adj = {v: set(g.neighbors(v)) for v in g.vertices}

    while stack:
        v = stack[-1]
        if temp_adj.get(v):
            u = next(iter(temp_adj[v]))
            temp_adj[v].remove(u)
            if not g.directed:
                temp_adj[u].discard(v)
            stack.append(u)
        else:
            path.append(stack.pop())

    path.reverse()
    return path if len(path) == len(g.vertices) + len(g.adjacency) else None

def spanning_tree(g: Graph, start: Optional[Any] = None) -> Optional[Graph]:
    if not g.vertices:
        return Graph()

    start = start or next(iter(g.vertices))
    visited = set()
    edges = []

    stack = [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        for neighbor in g.neighbors(v):
            if neighbor not in visited:
                w = g.weights.get((v, neighbor), 1.0)
                edges.append((v, neighbor, w))
                stack.append(neighbor)

    return Graph(vertices=list(g.vertices), weighted_edges=edges, directed=g.directed)

def minimum_spanning_tree(g: Graph) -> Optional[Graph]:
    if not g.vertices:
        return Graph()

    visited = set()
    edges = []
    start = next(iter(g.vertices))
    visited.add(start)
    edge_heap = [(g.weights.get((start, v), 1.0), start, v) for v in g.neighbors(start)]

    while edge_heap and len(visited) < len(g.vertices):
        weight, u, v = heapq.heappop(edge_heap)
        if v in visited:
            continue
        visited.add(v)
        edges.append((u, v, weight))
        for neighbor in g.neighbors(v):
            if neighbor not in visited:
                w = g.weights.get((v, neighbor), 1.0)
                heapq.heappush(edge_heap, (w, v, neighbor))

    if len(visited) == len(g.vertices):
        return Graph(vertices=list(g.vertices), weighted_edges=edges, directed=g.directed)
    return None

def graph_clique(g: Graph) -> List[Any]:
    if not g.vertices:
        return []

def is_complete(g: Graph) -> bool:
    n = len(g.vertices)
    for v in g.vertices:
        if g.degree(v) != n - 1:
            return False
    return True

def complement_graph(g: Graph) -> Graph:
    all_edges = [(u, v) for u in g.vertices for v in g.vertices if u != v]
    missing = [(u, v) for u, v in all_edges if v not in g.neighbors(u) or u not in g.neighbors(v)]
    comp = Graph(vertices=list(g.vertices), edges=missing, directed=g.directed)
    return comp