import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Graphviz Edge-Node Chart with NetworkX (Bidirectional Path Only, Colored Links)")

# Read DataFrame from CSV
df = pd.read_csv("D:/Workspace/VSCodePy/my-python-project/src/streamlit/input/network.csv")

first_node = st.text_input("Enter First Node", value="F CFV Summary View")#df["from"].iloc[0])

filter_mode = st.radio(
    "Last Node Filter Mode",
    ["Free text (comma separated)", "All reachable nodes from first node"]
)

if filter_mode == "Free text (comma separated)":
    last_nodes_text = st.text_input("Enter Last Node(s), comma separated", value="D Time, H Group Legal")#df["to"].iloc[-1])
    last_nodes = [node.strip() for node in last_nodes_text.split(",") if node.strip()]
else:
    # Use networkx to find all reachable nodes from first_node
    G_temp = nx.DiGraph()
    for _, row in df.iterrows():
        G_temp.add_edge(row["from"], row["to"])
        if row["flag"] == "Y":
            G_temp.add_edge(row["to"], row["from"])
    last_nodes = list(nx.descendants(G_temp, first_node))

# Build directed graph with attributes
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row["from"], row["to"], flag=row["flag"], join_type=row["join_type"])
    if row["flag"] == "Y":
        G.add_edge(row["to"], row["from"], flag=row["flag"], join_type=row["join_type"])

# Find all simple paths from first_node to any last_node
edges_in_paths = []
for last_node in last_nodes:
    try:
        for path in nx.all_simple_paths(G, source=first_node, target=last_node):
            for i in range(len(path)-1):
                edge_data = G.get_edge_data(path[i], path[i+1])
                edges_in_paths.append((path[i], path[i+1], edge_data["flag"], edge_data["join_type"]))
    except nx.NetworkXNoPath:
        continue

used_nodes = set()
for edge in edges_in_paths:
    used_nodes.add(edge[0])
    used_nodes.add(edge[1])

edges_in_paths = list({(e[0], e[1], e[2], e[3]) for e in edges_in_paths})

if not edges_in_paths:
    st.warning("No valid path found from the first node to the last node(s) with the current rules.")
else:
    if filter_mode == "Free text (comma separated)":
        # --- Graphviz Code ---
        graph_str = "digraph {\n"
        for node in used_nodes:
            graph_str += f'    "{node}" [shape=box, style=rounded]\n'

        color_map = {"left": "red", "inner": "green", "right": "blue"}
        for edge in edges_in_paths:
            from_node, to_node, flag, join_type = edge
            color = color_map["inner"] if flag == "Y" else color_map.get(join_type, "black")
            if flag == "Y":
                graph_str += f'    "{from_node}" -> "{to_node}" [color={color}]\n'
                graph_str += f'    "{to_node}" -> "{from_node}" [color={color}]\n'
            else:
                graph_str += f'    "{from_node}" -> "{to_node}" [color={color}]\n'
        graph_str += "}"

        st.graphviz_chart(graph_str)

    else:
        # --- PyVis Interactive Network ---
        net = Network(height="600px", width="100%", directed=True)
        color_map = {"left": "#00a6fb", "inner": "#e63946", "right": "#0077b6"}

        for node in used_nodes:
            if node == first_node:
                net.add_node(node, label=node, shape="box", color="#fca311", font={"size": 18})  # Gold, bigger font
            else:
                net.add_node(node, label=node, shape="box", color="#e5e5e5", font={"size": 12})  # Light yellow, normal font

        for edge in edges_in_paths:
            from_node, to_node, flag, join_type = edge
            color = color_map["inner"] if flag == "Y" else color_map.get(join_type, "black")
            net.add_edge(from_node, to_node, color=color, arrows="to")
            if flag == "Y":
                net.add_edge(to_node, from_node, color=color, arrows="to")

        net.set_options("""
{
  "nodes": {
    "font": {
      "size": 12
    }
  },
  "edges": {
    "color": {
      "inherit": false
    },
    "smooth": false,
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 0.5
      }
    }
  },
  "physics": {
    "enabled": true
  }
}
""")
        net.save_graph("network.html")
        HtmlFile = open("network.html", "r", encoding="utf-8")
        components.html(HtmlFile.read(), height=650, scrolling=True)