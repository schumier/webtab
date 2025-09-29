import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Graphviz Edge-Node Chart with NetworkX (Bidirectional Path Only, Colored Links)")

# Read DataFrame from CSV
df = pd.read_csv("D:/Workspace/VSCodePy/my-python-project/src/streamlit/input/network.csv")

show_mode = st.radio(
    "Visualization Mode",
    ["Normal network path", "Common network path between first nodes"]
)

# Allow multiple first nodes, comma separated
first_nodes_text = st.text_input("Enter First Node(s), comma separated", value="F CFV Summary View")
first_nodes = [node.strip() for node in first_nodes_text.split(",") if node.strip()]

if show_mode == "Normal network path":
    filter_mode = st.radio(
        "Last Node Filter Mode",
        ["Free text (comma separated)", "All reachable nodes from first node"]
    )
else:
    filter_mode = st.radio(
        "Graph shown as:",
        ["Include all connected nodes", "Only shown direct links"]
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
    last_nodes = list(nx.descendants(G_temp, first_nodes[0]))

# Build directed graph with attributes
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row["from"], row["to"], flag=row["flag"], join_type=row["join_type"])
    if row["flag"] == "Y":
        G.add_edge(row["to"], row["from"], flag=row["flag"], join_type=row["join_type"])

if show_mode == "Normal network path":
    if filter_mode == "All reachable nodes from first node":
        all_edges_in_paths = []
        all_used_nodes = set()
        for first_node in first_nodes:
            reachable_nodes = nx.descendants(G, first_node)
            for target in reachable_nodes:
                try:
                    for path in nx.all_simple_paths(G, source=first_node, target=target):
                        for i in range(len(path)-1):
                            edge_data = G.get_edge_data(path[i], path[i+1])
                            all_edges_in_paths.append((path[i], path[i+1], edge_data["flag"], edge_data["join_type"]))
                except nx.NetworkXNoPath:
                    continue
        # Remove duplicate edges
        all_edges_in_paths = list({(e[0], e[1], e[2], e[3]) for e in all_edges_in_paths})
        for edge in all_edges_in_paths:
            all_used_nodes.add(edge[0])
            all_used_nodes.add(edge[1])

        if not all_edges_in_paths:
            st.warning("No valid path found from the first node(s) to any reachable node.")
        else:
            # --- PyVis Interactive Network ---
            net = Network(height="600px", width="100%", directed=True)
            color_map = {"left": "#00a6fb", "inner": "#e63946", "right": "#0077b6"}

            for node in all_used_nodes:
                if node in first_nodes:
                    net.add_node(node, label=node, shape="box", color="#fca311", font={"size": 18})  # Gold, bigger font
                else:
                    net.add_node(node, label=node, shape="box", color="#e5e5e5", font={"size": 12})  # Light yellow, normal font

            for edge in all_edges_in_paths:
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
    else:
        all_edges_in_paths = []
        all_used_nodes = set()
        for first_node in first_nodes:
            for last_node in last_nodes:
                try:
                    for path in nx.all_simple_paths(G, source=first_node, target=last_node):
                        for i in range(len(path)-1):
                            edge_data = G.get_edge_data(path[i], path[i+1])
                            all_edges_in_paths.append((path[i], path[i+1], edge_data["flag"], edge_data["join_type"]))
                            all_used_nodes.add(path[i])
                            all_used_nodes.add(path[i+1])
                except nx.NetworkXNoPath:
                    continue

        all_edges_in_paths = list({(e[0], e[1], e[2], e[3]) for e in all_edges_in_paths})

        if not all_edges_in_paths:
            st.warning("No valid path found from the first node(s) to the last node(s) with the current rules.")
        else:
            if filter_mode == "Free text (comma separated)":
                # --- Graphviz Code ---
                graph_str = "digraph {\n"
                for node in all_used_nodes:
                    graph_str += f'    "{node}" [shape=box, style=rounded]\n'

                color_map = {"left": "red", "inner": "green", "right": "blue"}
                for edge in all_edges_in_paths:
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

                for node in all_used_nodes:
                    if node in first_nodes:
                        net.add_node(node, label=node, shape="box", color="#fca311", font={"size": 18})  # Gold, bigger font
                    else:
                        net.add_node(node, label=node, shape="box", color="#e5e5e5", font={"size": 12})  # Light yellow, normal font

                for edge in all_edges_in_paths:
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
else:

    if filter_mode == "Include all connected nodes":
        # --- Common Network Path Visualization ---
        st.subheader("Common Network Path(s) Between First Nodes")

        # 1. Find all reachable nodes for each first node
        reachable_nodes_per_first = []
        for first_node in first_nodes:
            reachable = set(nx.descendants(G, first_node))
            reachable_nodes_per_first.append(reachable)

        # 2. Find intersection: nodes reachable from all first nodes
        if reachable_nodes_per_first:
            common_targets = set.intersection(*reachable_nodes_per_first)
        else:
            common_targets = set()

        # 3. For each first node, find all paths to each common reachable node
        common_edges = set()
        for first_node in first_nodes:
            for target in common_targets:
                try:
                    for path in nx.all_simple_paths(G, source=first_node, target=target):
                        for i in range(len(path)-1):
                            edge_data = G.get_edge_data(path[i], path[i+1])
                            common_edges.add((path[i], path[i+1], edge_data["flag"], edge_data["join_type"]))
                except nx.NetworkXNoPath:
                    continue

        # 4. Collect all nodes used in these paths
        used_nodes = set()
        for edge in common_edges:
            used_nodes.add(edge[0])
            used_nodes.add(edge[1])
        for node in first_nodes:
            used_nodes.add(node)

        if common_edges:
            net_common = Network(height="400px", width="100%", directed=True)
            color_map = {"left": "#00a6fb", "inner": "#e63946", "right": "#0077b6"}
            for node in used_nodes:
                if node in first_nodes:
                    net_common.add_node(node, label=node, shape="box", color="#fca311", font={"size": 18})
                else:
                    net_common.add_node(node, label=node, shape="box", color="#bde0fe", font={"size": 12})
            for edge in common_edges:
                from_node, to_node, flag, join_type = edge
                color = color_map["inner"] if flag == "Y" else color_map.get(join_type, "black")
                net_common.add_edge(from_node, to_node, color=color, arrows="to")
                if flag == "Y":
                    net_common.add_edge(to_node, from_node, color=color, arrows="to")
            net_common.set_options("""
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
        "scaleFactor": 1
    }
    }
},
"physics": {
    "enabled": true
}
}
""")
            net_common.save_graph("network_common.html")
            HtmlFile = open("network_common.html", "r", encoding="utf-8")
            components.html(HtmlFile.read(), height=450, scrolling=True)
        else:
            st.info("No common network path found between the selected first nodes.")
    elif filter_mode == "Only shown direct links":
        # --- Common Direct Target Visualization ---
        st.subheader("Common Direct Target(s) of First Nodes")

        # 1. Find direct targets for each first node
        direct_targets_per_first = []
        for first_node in first_nodes:
            direct_targets = set(G.successors(first_node))
            direct_targets_per_first.append(direct_targets)

        # 2. Find intersection: nodes directly connected from all first nodes
        if direct_targets_per_first:
            common_direct_targets = set.intersection(*direct_targets_per_first)
        else:
            common_direct_targets = set()

        # 3. Collect edges from each first node to each common direct target
        common_edges = set()
        for first_node in first_nodes:
            for target in common_direct_targets:
                edge_data = G.get_edge_data(first_node, target)
                if edge_data:
                    common_edges.add((first_node, target, edge_data["flag"], edge_data["join_type"]))

        # 4. Collect all nodes used in these edges
        used_nodes = set(first_nodes)
        used_nodes.update(common_direct_targets)

        if common_edges:
            net_common = Network(height="400px", width="100%", directed=True)
            color_map = {"left": "#00a6fb", "inner": "#e63946", "right": "#0077b6"}
            for node in used_nodes:
                if node in first_nodes:
                    net_common.add_node(node, label=node, shape="box", color="#fca311", font={"size": 18})
                else:
                    net_common.add_node(node, label=node, shape="box", color="#bde0fe", font={"size": 12})
            for edge in common_edges:
                from_node, to_node, flag, join_type = edge
                color = color_map["inner"] if flag == "Y" else color_map.get(join_type, "black")
                net_common.add_edge(from_node, to_node, color=color, arrows="to")
                if flag == "Y":
                    net_common.add_edge(to_node, from_node, color=color, arrows="to")
            net_common.set_options("""
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
        "scaleFactor": 1
    }
    }
},
"physics": {
    "enabled": true
}
}
""")
            net_common.save_graph("network_common.html")
            HtmlFile = open("network_common.html", "r", encoding="utf-8")
            components.html(HtmlFile.read(), height=450, scrolling=True)
        else:
            st.info("No common direct target found between the selected first nodes.")