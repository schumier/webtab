import streamlit as st
import pandas as pd
import networkx as nx

st.title("Graphviz Edge-Node Chart with NetworkX (Bidirectional Path Only, Colored Links)")

df = pd.DataFrame({
    "from": ["F CFV Summary View", "R Entity to Facility","R Entity to Facility", "F CFV Detail View", "F CFV Detail View", "D Account", "D Treasury Deal","F CFV Detail View"],
    "to":   ["D Facillity","D Facillity", "D Party", "D Party", "D Account", "D Country", "F Instrument","D Treasury Deal"],
    "flag": ["N", "Y","N", "N", "N", "Y", "N","N"],
    "join_type": ["left", "inner","left", "right", "left", "inner", "right", "left"]
})

first_node = st.text_input("Enter First Node", value=df["from"].iloc[0])
last_nodes_text = st.text_input("Enter Last Node(s), comma separated", value=df["to"].iloc[-1])
last_nodes = [node.strip() for node in last_nodes_text.split(",") if node.strip()]

# Build directed graph
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row["from"], row["to"], flag=row["flag"], join_type=row["join_type"])
    # If bidirectional, add reverse edge
    if row["flag"] == "Y":
        G.add_edge(row["to"], row["from"], flag=row["flag"], join_type=row["join_type"])

# Find all simple paths from first_node to any last_node
edges_in_paths = []
for last_node in last_nodes:
    for path in nx.all_simple_paths(G, source=first_node, target=last_node):
        # Collect edges in the path
        for i in range(len(path)-1):
            edge_data = G.get_edge_data(path[i], path[i+1])
            edges_in_paths.append((path[i], path[i+1], edge_data["flag"], edge_data["join_type"]))

used_nodes = set()
for edge in edges_in_paths:
    used_nodes.add(edge[0])
    used_nodes.add(edge[1])

# After collecting edges_in_paths
edges_in_paths = list({(e[0], e[1], e[2], e[3]) for e in edges_in_paths})

if not edges_in_paths:
    st.warning("No valid path found from the first node to the last node(s) with the current rules.")
else:
    graph_str = "digraph {\n"
    for node in used_nodes:
        graph_str += f'    "{node}" [shape=box, style=rounded]\n'

    color_map = {"left": "red", "inner": "green", "right": "blue"}
    for edge in edges_in_paths:
        from_node, to_node, flag, join_type = edge
        color = color_map["inner"] if flag == "Y" else color_map.get(join_type, "black")
        if flag == "Y":
            # Draw two separate edges for bidirectional
            graph_str += f'    "{from_node}" -> "{to_node}" [color={color}]\n'
            graph_str += f'    "{to_node}" -> "{from_node}" [color={color}]\n'
        else:
            graph_str += f'    "{from_node}" -> "{to_node}" [color={color}]\n'
    graph_str += "}"

    st.graphviz_chart(graph_str)