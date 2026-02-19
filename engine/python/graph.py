"""
Graph Data Structures and Basic Algorithms
Python implementation for learning and prototyping
"""

from collections import defaultdict, deque
import heapq
from typing import List, Tuple, Dict, Set, Optional
import math


class Graph:
    """
    Weighted directed graph implementation using adjacency list
    """
    
    def __init__(self, vertices: int = 0):
        self.V = vertices
        self.adj = defaultdict(list)  # Adjacency list: {node: [(neighbor, weight), ...]}
        self.edges = []  # List of all edges for certain algorithms
        
    def add_vertex(self, v: int):
        """Add a vertex to the graph"""
        if v >= self.V:
            self.V = v + 1
        if v not in self.adj:
            self.adj[v] = []
    
    def add_edge(self, u: int, v: int, weight: float = 1.0):
        """
        Add a weighted edge from u to v
        For undirected graph, call this twice: add_edge(u,v) and add_edge(v,u)
        """
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, weight))
        self.edges.append((u, v, weight))
    
    def dijkstra(self, source: int) -> Dict[int, float]:
        """
        Dijkstra's shortest path algorithm
        
        Args:
            source: Starting vertex
            
        Returns:
            Dictionary of shortest distances from source to all vertices
            
        Time Complexity: O((V + E) log V)
        """
        # Initialize distances
        dist = {i: float('inf') for i in range(self.V)}
        dist[source] = 0
        
        # Priority queue: (distance, vertex)
        pq = [(0, source)]
        visited = set()
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if u in visited:
                continue
            
            visited.add(u)
            
            # Check all neighbors
            for v, weight in self.adj[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    heapq.heappush(pq, (dist[v], v))
        
        return dist
    
    def get_shortest_path(self, source: int, target: int) -> Tuple[List[int], float]:
        """
        Get the shortest path between two vertices
        
        Args:
            source: Starting vertex
            target: Destination vertex
            
        Returns:
            Tuple of (path as list of vertices, total distance)
        """
        dist = {i: float('inf') for i in range(self.V)}
        parent = {i: None for i in range(self.V)}
        dist[source] = 0
        
        pq = [(0, source)]
        visited = set()
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if u == target:
                break
            
            if u in visited:
                continue
            
            visited.add(u)
            
            for v, weight in self.adj[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))
        
        # Reconstruct path
        if dist[target] == float('inf'):
            return [], float('inf')
        
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        
        return path, dist[target]
    
    def bfs(self, source: int) -> Dict[int, int]:
        """
        Breadth-First Search
        
        Args:
            source: Starting vertex
            
        Returns:
            Dictionary of distances (in number of edges) from source
        """
        visited = {source}
        queue = deque([(source, 0)])
        distances = {source: 0}
        
        while queue:
            u, dist = queue.popleft()
            
            for v, _ in self.adj[u]:
                if v not in visited:
                    visited.add(v)
                    distances[v] = dist + 1
                    queue.append((v, dist + 1))
        
        return distances
    
    def dfs(self, source: int, visited: Optional[Set[int]] = None) -> List[int]:
        """
        Depth-First Search
        
        Args:
            source: Starting vertex
            visited: Set of already visited vertices (for recursion)
            
        Returns:
            List of vertices in DFS order
        """
        if visited is None:
            visited = set()
        
        visited.add(source)
        traversal = [source]
        
        for v, _ in self.adj[u]:
            if v not in visited:
                traversal.extend(self.dfs(v, visited))
        
        return traversal


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    
    Args:
        lat1, lon1: Latitude and longitude of first point (in degrees)
        lat2, lon2: Latitude and longitude of second point (in degrees)
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return c * r


def build_graph_from_locations(locations: List[Dict]) -> Graph:
    """
    Build a graph from a list of geographic locations
    
    Args:
        locations: List of dicts with 'id', 'lat', 'lon' keys
        
    Returns:
        Complete graph where edge weights are distances between locations
    """
    n = len(locations)
    g = Graph(n)
    
    # Create complete graph with haversine distances
    for i in range(n):
        for j in range(i + 1, n):
            loc1 = locations[i]
            loc2 = locations[j]
            
            distance = haversine_distance(
                loc1['lat'], loc1['lon'],
                loc2['lat'], loc2['lon']
            )
            
            # Add edges in both directions (undirected graph)
            g.add_edge(i, j, distance)
            g.add_edge(j, i, distance)
    
    return g


# Example usage and testing
if __name__ == "__main__":
    print("🔬 Testing Graph Algorithms\n")
    
    # Create a sample graph
    print("Creating sample road network...")
    g = Graph(6)
    
    # Add edges (representing roads with distances in km)
    edges = [
        (0, 1, 10.0),  # Depot to Location 1: 10km
        (0, 2, 5.0),   # Depot to Location 2: 5km
        (1, 3, 1.0),   # Location 1 to 3: 1km
        (2, 1, 3.0),   # Location 2 to 1: 3km
        (2, 3, 9.0),   # Location 2 to 3: 9km
        (3, 4, 2.0),   # Location 3 to 4: 2km
        (1, 4, 7.0),   # Location 1 to 4: 7km
        (4, 5, 4.0),   # Location 4 to 5: 4km
    ]
    
    for u, v, w in edges:
        g.add_edge(u, v, w)
    
    print(f"Graph created with {g.V} vertices and {len(g.edges)} edges\n")
    
    # Test Dijkstra's algorithm
    print("=" * 50)
    print("Testing Dijkstra's Shortest Path Algorithm")
    print("=" * 50)
    
    source = 0
    distances = g.dijkstra(source)
    
    print(f"\nShortest distances from vertex {source} (Depot):")
    for node in sorted(distances.keys()):
        if distances[node] == float('inf'):
            print(f"  To Location {node}: Unreachable")
        else:
            print(f"  To Location {node}: {distances[node]:.2f} km")
    
    # Test path finding
    print("\n" + "=" * 50)
    print("Testing Path Finding")
    print("=" * 50)
    
    source, target = 0, 5
    path, distance = g.get_shortest_path(source, target)
    
    if path:
        print(f"\nShortest path from {source} to {target}:")
        print(f"  Route: {' → '.join(map(str, path))}")
        print(f"  Total distance: {distance:.2f} km")
    else:
        print(f"\nNo path found from {source} to {target}")
    
    # Test with real coordinates
    print("\n" + "=" * 50)
    print("Testing with Real Geographic Coordinates")
    print("=" * 50)
    
    # Sample locations in San Francisco Bay Area
    locations = [
        {"id": "Depot", "lat": 37.7749, "lon": -122.4194},      # SF
        {"id": "Customer1", "lat": 37.8044, "lon": -122.2712},  # Oakland
        {"id": "Customer2", "lat": 37.3861, "lon": -122.0839},  # Mountain View
        {"id": "Customer3", "lat": 37.6879, "lon": -122.4702},  # Daly City
    ]
    
    print("\nBuilding graph from coordinates...")
    geo_graph = build_graph_from_locations(locations)
    
    print(f"Created graph with {len(locations)} locations")
    
    # Find shortest distances from depot
    distances = geo_graph.dijkstra(0)
    
    print("\nDistances from Depot (San Francisco):")
    for i, loc in enumerate(locations):
        if i == 0:
            continue
        print(f"  To {loc['id']}: {distances[i]:.2f} km")
    
    print("\n✅ All tests completed successfully!")
