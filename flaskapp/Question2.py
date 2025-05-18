import networkx as nx
import matplotlib.pyplot as plt
import random

# --- Step 1: Generate Graph ---
G = nx.Graph()
nodes = list(range(10))
G.add_nodes_from(nodes)

edges_to_add = random.randint(10, 14)
while G.number_of_edges() < edges_to_add:
    n1, n2 = random.sample(nodes, 2)
    G.add_edge(n1, n2)

# --- Step 2: Print adjacency list ---
adj_dict = {node: list(G.adj[node]) for node in G.nodes()}
for node, neighbors in adj_dict.items():
    print(f"{node}: {neighbors}")

# --- Step 3: Visualize the graph ---
pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(8, 6))
nx.draw_networkx_nodes(G, pos, node_size=500)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, font_size=12)
plt.title("Randomly Generated Graph with 10 Nodes", fontsize=16)
plt.axis('off')
plt.show()

# --- Step 4: Define search class ---
class GraphSearch:
    def __init__(self, graph):
        self.graph = graph

    def dfs(self, start):
        """Depth-First Search (Recursive implementation)"""
        visited = set()
        result = []

        def _dfs(v):
            visited.add(v)
            result.append(v)
            for neighbor in self.graph[v]:
                if neighbor not in visited:
                    _dfs(neighbor)

        _dfs(start)
        return result

    def level_order(self, start):
        """Level-Order Traversal (Breadth-First Search)"""
        visited = set()
        queue = [start]
        result = []

        visited.add(start)

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

search = GraphSearch(adj_dict)
start_node = 0

# Run DFS and Level-Order (BFS)
dfs_result = search.dfs(start_node)
bfs_result = search.level_order(start_node)

# Print the results
print("\nDFS Traversal:", dfs_result)
print("Level-Order Traversal:", bfs_result)

# 2-line observation
print("\nObservation:")
print("DFS dives deep along one path before backtracking.")
print("Level-Order visits all nodes level by level, starting from the root.")

## Part b

# --- Step 1: Get degrees for all nodes ---
degrees = {node: len(neighbors) for node, neighbors in adj_dict.items() if len(neighbors) > 0}

# --- Step 2: Compute lambda (Lagrange multiplier) ---
Bt = 10
n = len(degrees)
degree_inverse_sum = sum(1 / d for d in degrees.values())
lambda_val = n / (Bt + degree_inverse_sum)

# --- Step 3: Compute optimal budget allocation for each node ---
x_star = {node: (1 / lambda_val) - (1 / d) for node, d in degrees.items()}

# --- Step 4: Plot bar chart ---
nodes = list(x_star.keys())
budgets = [x_star[node] for node in nodes]
labels = [f"{node}\nd={degrees[node]}" for node in nodes]  # show degree on each bar

plt.figure(figsize=(10, 6))
bars = plt.bar(nodes, budgets, tick_label=labels, color='skyblue')
plt.ylabel('Budget Allocation $x_i^*$')
plt.xlabel('Node (with degree)')
plt.title('Optimal Budget Allocation ($B_t = 10$)')
plt.grid(True, axis='y')

# Optional: Add exact budget values on top of bars
for bar, node in zip(bars, nodes):
    yval = x_star[node]
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f"{yval:.2f}", ha='center', fontsize=8)

plt.tight_layout()
print("x_star =", x_star)
plt.show()

