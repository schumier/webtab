import streamlit as st
import pandas as pd

st.title("Graphviz Edge-Node Chart from DataFrame (Conditional Bidirectional, Colored Links)")

# Example DataFrame with 'from', 'to', 'flag', and 'join_type' columns
df = pd.DataFrame({
    "from": ["F CFV Summary View", "R Entity to Party", "F CFV Detail View", "F CFV Detail View", "D Account", "D Treasury Deal","F CFV Detail View"],
    "to":   ["D Party", "D Party", "D Party", "D Account", "D Country", "F Instrument","D Treasury Deal"],
    "flag": ["N", "Y", "N", "N", "Y", "N","N"],
    "join_type": ["left", "inner", "right", "left", "inner", "right", "left"]
})

# Free text input for first and last node
first_node = st.text_input("Enter First Node", value=df["from"].iloc[0])
last_node = st.text_input("Enter Last Node", value=df["to"].iloc[-1])

# Only edges from first_node to last_node, or bidirectional to last_node
filtered_df = df[((df["from"] == first_node) & (df["to"] == last_node)) |
                 ((df["to"] == last_node) & (df["flag"] == "Y"))]

# Only add nodes that are actually used in filtered edges
used_nodes = set(filtered_df["from"]).union(set(filtered_df["to"]))
graph_str = "digraph {\n"
for node in used_nodes:
    graph_str += f'    "{node}" [shape=box, style=rounded]\n'

# Define color mapping
color_map = {"left": "red", "inner": "green", "right": "blue"}

for _, row in filtered_df.iterrows():
    # If flag is Y, treat join_type as 'inner' for both directions
    if row["flag"] == "Y":
        color = color_map["inner"]
        graph_str += f'    "{row["from"]}" -> "{row["to"]}" [color={color}]\n'
        graph_str += f'    "{row["to"]}" -> "{row["from"]}" [color={color}]\n'
    else:
        color = color_map.get(row["join_type"], "black")
        graph_str += f'    "{row["from"]}" -> "{row["to"]}" [color={color}]\n'
graph_str += "}"

st.graphviz_chart(graph_str)