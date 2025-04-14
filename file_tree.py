import os
import networkx as nx
import matplotlib.pyplot as plt

# Get the absolute path of the current directory
root_dir = os.path.abspath(".")  # Fix: Use the current directory

# Check if directory exists
if not os.path.exists(root_dir):
    raise FileNotFoundError(f"Directory '{root_dir}' not found. Check your path!")

# Create a directed graph
G = nx.DiGraph()

# Function to add nodes and edges to the graph
def add_nodes_edges(directory, parent=None):
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            G.add_edge(directory if parent is None else parent, item_path)  # Add edge
            if os.path.isdir(item_path):  # If directory, recurse
                add_nodes_edges(item_path, item_path)
    except PermissionError:
        print(f"⚠️ Skipping {directory}: Permission Denied")

# Build the graph
add_nodes_edges(root_dir)

# Plot the graph
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, k=0.5)  # Adjust k for better spacing
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", edge_color="gray", font_size=8, font_weight="bold", arrows=True)

plt.title("WealthBot Directory Structure")
plt.show()
