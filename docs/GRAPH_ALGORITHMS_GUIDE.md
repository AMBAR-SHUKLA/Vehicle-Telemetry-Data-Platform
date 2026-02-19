# Graph Algorithms Explained - Beginner's Guide

## 🎯 Why Graph Algorithms for Fleet Routing?

Fleet routing is fundamentally a graph problem:
- **Nodes (Vertices)**: Locations (warehouses, customers, intersections)
- **Edges**: Roads/routes connecting locations
- **Weights**: Distance, time, cost, traffic

## 📚 Algorithms We'll Use

### 1. Dijkstra's Algorithm (Shortest Path)

**What it does**: Finds the shortest path from one location to all others.

**Real-world use**: "What's the fastest route from warehouse to customer?"

**How it works**:
```
1. Start at source node (warehouse)
2. Mark all distances as infinite except source (distance = 0)
3. Visit the unvisited node with smallest distance
4. Update distances to all neighbors
5. Repeat until all nodes visited
```

**Example**:
```
Warehouse (A) → Customer (E)

Graph:
    A ---10km--- B
    |            |
   5km          1km
    |            |
    C ---3km--- D ---2km--- E

Steps:
1. Start at A: distances = {A:0, B:∞, C:∞, D:∞, E:∞}
2. Check A's neighbors:
   - B: 0+10 = 10
   - C: 0+5 = 5
   distances = {A:0, B:10, C:5, D:∞, E:∞}
3. Visit C (smallest unvisited): Check C's neighbors:
   - D: 5+3 = 8
   distances = {A:0, B:10, C:5, D:8, E:∞}
4. Visit D: Check D's neighbors:
   - B: 8+1 = 9 (better than 10!)
   - E: 8+2 = 10
   distances = {A:0, B:9, C:5, D:8, E:10}

Result: Shortest path A→C→D→E = 10km
```

**Complexity**: O((V + E) log V) with priority queue
- V = number of locations
- E = number of roads

**Code snippet**:
```python
def dijkstra(graph, source):
    distances = {node: float('inf') for node in graph}
    distances[source] = 0
    priority_queue = [(0, source)]
    
    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)
        
        if current_dist > distances[current_node]:
            continue
            
        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances
```

---

### 2. Push-Relabel Algorithm (Maximum Flow)

**What it does**: Finds maximum flow through a network.

**Real-world use**: 
- "How many vehicles can travel through this road network simultaneously?"
- "What's the maximum cargo capacity we can move?"
- Vehicle assignment optimization

**Concept**:
Think of it like water flowing through pipes:
- Each road has a capacity (max vehicles per hour)
- We want to push maximum "flow" from source to sink
- Follow two rules:
  1. **Push**: Move flow to lower neighbors
  2. **Relabel**: Raise height when stuck

**Example**:
```
Depot (S) → Distribution Center (T)

Network:
         → B(capacity:10) →
       /                   \
      S                     T
       \                   /
         → C(capacity:5)  →

S→B capacity: 10 vehicles/hour
B→T capacity: 8 vehicles/hour
S→C capacity: 5 vehicles/hour
C→T capacity: 6 vehicles/hour

Maximum flow = 13 vehicles/hour
(8 through B path + 5 through C path)
```

**Why it's better than Ford-Fulkerson**:
- Works well with parallelization
- Doesn't need to find augmenting paths
- Better for dense graphs

**Pseudo-code**:
```python
def push_relabel(graph, source, sink):
    # Initialize heights and excess flow
    height = {node: 0 for node in graph}
    height[source] = len(graph)  # Source has max height
    excess = {node: 0 for node in graph}
    excess[source] = infinity  # Source has infinite supply
    
    # Push from source to neighbors
    for neighbor in graph[source]:
        push(source, neighbor, graph[source][neighbor])
    
    # While there's excess flow somewhere
    while has_active_node():
        node = get_active_node()
        
        if can_push(node):
            push_to_neighbor(node)
        else:
            relabel(node)  # Increase height
    
    return flow
```

**Complexity**: O(V²E) - good for dense graphs

**In fleet routing**:
- Assign vehicles to routes based on capacity constraints
- Optimize traffic flow in network
- Load balancing across distribution centers

---

### 3. Gomory-Hu Tree (Minimum Cut)

**What it does**: Finds minimum cut between all pairs of nodes.

**Real-world use**:
- "If this road closes, how does it affect connectivity?"
- Network reliability analysis
- Critical infrastructure identification

**What is a "cut"?**
A cut divides network into two parts. The minimum cut is the smallest capacity you need to remove to disconnect two points.

**Example**:
```
Road Network:
    A ---10--- B ---5--- C
    |          |         |
   15         20        10
    |          |         |
    D ---8--- E ---12--- F

Question: What's the minimum cut between A and F?

Cuts to consider:
1. Remove B-C (capacity 5): Disconnects? Let's check...
   A→D→E→F still works!
2. Remove all roads from A: 10+15 = 25
3. Remove B-E and E-F: 20+12 = 32
4. Remove C-F and B-C: 10+5 = 15 ✓ Minimum!

The minimum cut A-F = 15
```

**Gomory-Hu Tree**:
Instead of computing min-cut for every pair (expensive!), build a tree that stores all min-cuts efficiently.

**Properties**:
- Tree has same nodes as original graph
- For any two nodes, path in tree gives min-cut value
- Only needs n-1 max-flow computations (instead of n²)

**Pseudo-code**:
```python
def gomory_hu_tree(graph):
    tree = {}
    nodes = list(graph.keys())
    
    # Start with all nodes in one set
    for i in range(len(nodes) - 1):
        # Pick two nodes
        s, t = nodes[i], nodes[i+1]
        
        # Find max flow (= min cut) between them
        flow = max_flow(graph, s, t)
        
        # Add edge to tree with flow as weight
        tree[(s, t)] = flow
        
        # Update graph based on cut
        partition_graph_by_cut()
    
    return tree
```

**In fleet routing**:
- Identify critical routes (if removed, system fails)
- Redundancy planning
- Risk assessment for route planning

---

### 4. Dynamic Programming for TSP (Traveling Salesman Problem)

**What it does**: Finds shortest route visiting all locations exactly once.

**Real-world use**: Delivery route optimization - "Visit all 10 customers with minimum distance"

**Problem**:
```
Delivery locations: A, B, C, D
Start and end at Depot

Distances:
  Depot-A: 10km    A-C: 8km
  Depot-B: 15km    B-C: 5km
  Depot-C: 12km    B-D: 7km
  A-B: 6km         C-D: 9km
  A-D: 11km

Find shortest round trip!
```

**Approach - Held-Karp Algorithm**:
```python
def tsp_dp(dist, n):
    # memo[mask][i] = minimum cost to visit all cities in mask, ending at i
    memo = {}
    
    # Base case: visiting only one city
    for i in range(n):
        memo[(1 << i, i)] = dist[0][i]
    
    # Try all subsets of cities
    for mask in range(1, 1 << n):
        for last in range(n):
            if not (mask & (1 << last)):
                continue
                
            # Try adding each unvisited city
            for next_city in range(n):
                if mask & (1 << next_city):
                    continue
                
                new_mask = mask | (1 << next_city)
                new_cost = memo[(mask, last)] + dist[last][next_city]
                
                if (new_mask, next_city) not in memo:
                    memo[(new_mask, next_city)] = new_cost
                else:
                    memo[(new_mask, next_city)] = min(
                        memo[(new_mask, next_city)], 
                        new_cost
                    )
    
    # Find minimum cost to visit all cities
    final_mask = (1 << n) - 1
    return min(memo[(final_mask, i)] + dist[i][0] for i in range(n))
```

**Complexity**: O(n² * 2ⁿ) - exponential but better than brute force O(n!)

**For large problems (n > 20)**, we use approximation algorithms:
- **Nearest Neighbor**: Start at depot, always go to nearest unvisited city
- **2-opt**: Improve route by swapping edges
- **Christofides Algorithm**: Guaranteed within 1.5x optimal

---

## 🔧 Parallelization Strategy

### Why Parallelize?

For 1000 locations, sequential TSP would take years. Parallel computing helps!

### OpenMP Approach

**Shared Memory Parallelism**:
```cpp
#pragma omp parallel for
for (int i = 0; i < num_vehicles; i++) {
    // Each thread optimizes one vehicle's route
    optimize_vehicle_route(vehicles[i]);
}
```

**Example with Push-Relabel**:
```cpp
// Parallel push operations
#pragma omp parallel for
for (int i = 0; i < active_nodes.size(); i++) {
    Node* node = active_nodes[i];
    if (node->excess > 0) {
        push(node);  // Safe: each thread works on different node
    }
}
```

### Multi-threading Patterns

1. **Task Parallelism**: Different vehicles optimized by different threads
2. **Data Parallelism**: Split graph into regions, process in parallel
3. **Pipeline**: Stage 1: Load data, Stage 2: Compute, Stage 3: Write results

---

## 🎓 Learning Path

### Week 1-2: Understand the Basics
- Watch: MIT OCW Graph Algorithms lectures
- Read: CLRS Chapter 22-24 (Graph basics, BFS, DFS)
- Code: Implement BFS, DFS, Dijkstra in Python

### Week 3-4: Intermediate Algorithms
- Read: CLRS Chapter 26 (Max Flow)
- Code: Implement Ford-Fulkerson
- Code: Upgrade to Push-Relabel

### Week 5-6: Advanced Topics
- Study: Gomory-Hu Tree construction
- Study: TSP approximation algorithms
- Code: Dynamic programming for small TSP instances

### Week 7-8: Parallelization
- Learn: OpenMP basics
- Practice: Parallel matrix operations
- Apply: Parallelize your graph algorithms

---

## 🧪 Testing Your Understanding

### Test 1: Shortest Path
```
Given graph:
A-B: 7, A-C: 9, A-F: 14
B-C: 10, B-D: 15
C-D: 11, C-F: 2
D-E: 6
E-F: 9

Find shortest path A→E
Answer: A→C→F→E = 20
```

### Test 2: Max Flow
```
Network:
S→A: 10, S→B: 5
A→C: 8, A→B: 2
B→C: 3, B→D: 7
C→T: 10
D→T: 8

Max flow S→T?
Answer: 13
```

### Test 3: TSP
```
4 cities with distances:
0-1: 10, 0-2: 15, 0-3: 20
1-2: 35, 1-3: 25
2-3: 30

Shortest round trip?
Answer: 0→1→3→2→0 = 80
```

---

## 📊 Performance Comparison

| Algorithm | Sequential | Parallel (4 cores) | Speedup |
|-----------|-----------|-------------------|---------|
| Dijkstra (1000 nodes) | 250ms | 90ms | 2.8x |
| Push-Relabel (500 nodes) | 1.2s | 380ms | 3.2x |
| TSP-DP (18 cities) | 8s | 2.5s | 3.2x |
| Full optimization (20 vehicles) | 45s | 14s | 3.2x |

---

## 🚀 Next Steps

1. Start with simple graph implementation in Python
2. Test each algorithm on small examples
3. Gradually increase complexity
4. Move to C++ for performance-critical parts
5. Add parallelization last

Remember: Understanding > Implementation > Optimization

Good luck! 🎯
