import streamlit as st
from graphviz_wrap import show_graphviz_app
from other_wrap import show_other_wrap_app

# Sidebar navigation
page = st.sidebar.selectbox("Select Page", ["Dashboard", "Graph Visualization"])

if page == "Dashboard":
    # ... your dashboard code ...
    show_other_wrap_app()
elif page == "Graph Visualization":
    show_graphviz_app()