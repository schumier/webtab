import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Sample Dashboard", layout="wide")

st.title("📊 Sample Streamlit Dashboard")

st.markdown("*Streamlit* is **really** ***cool***.")
st.markdown('''
    :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
    :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
st.markdown("Here's a bouquet &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''If you end a line with two spaces,
a soft return is used for the next line.

Two (or more) newline characters in a row will result in a hard return.
'''
st.markdown(multi)

# Sample app ranking data
app_data = pd.DataFrame({
    "Rank": [1, 2, 3, 4, 5, 6, 7],
    "Preview": [
        "GPTZero", "MathGPT", "KnowledgeGPT", "Tweet generator",
        "BERT Semantic Int", "GPTflix", "GPT Lab Lounge"
    ],
    "App name": [
        "GPTZero", "MathGPT", "KnowledgeGPT", "Tweet generator",
        "BERT Semantic Int", "GPTflix", "GPT Lab Lounge"
    ],
    "Avatar": [
        "etEdward", "napoleon.such", "mmz-001", "kinosal",
        "searchsolved", "stephanshurgers", "dcidin"
    ],
    "Owner": [
        "etEdward", "napoleon.such", "mmz-001", "kinosal",
        "searchsolved", "stephanshurgers", "dcidin"
    ],
    "URL": [
        "https://gpt", "https://math", "https://kn", "https://tw",
        "https://bert", "https://gptf", "https://gptl"
    ],
    "Views": [
        "463k", "79k", "883", "15k", "12k", "12k", "4k"
    ],
    "GitHub": [
        "⭐", "⭐", "⭐", "⭐", "⭐", "⭐", "⭐"
    ],
    "Views (past 30 days)": [
        "📈", "📈", "📈", "📈", "📈", "📈", "📈"
    ]
})

# Calculate % of views (max = 450k)
def parse_views(val):
    if 'k' in val:
        return float(val.replace('k', '')) * 1000
    else:
        return float(val)

app_data["Views_num"] = app_data["Views"].apply(parse_views)
app_data["Views %"] = (app_data["Views_num"] / 450_000 * 100).round(2)

# Sidebar filter for App name
st.sidebar.header("Filter")
selected_apps = st.sidebar.multiselect(
    "Select App name(s)",
    options=app_data["App name"].tolist(),
    default=app_data["App name"].tolist()
)

filtered_data = app_data[app_data["App name"].isin(selected_apps)].copy()

# Add a simple bar chart as HTML in the table for Views %
def bar_html(percent):
    bar_width = int(percent * 0.52)  # scale for visual (max 200px for 100%)
    color = "#4CAF50"
    # Remove any newlines from the HTML string
    html = (
        f"<div style='background: #eee; width: 100%; height: 18px; position: relative; border-radius: 4px;'>"
        f"<div style='background: {color}; width: {bar_width}px; height: 18px; border-radius: 4px;'></div>"
        f"<div style='position: absolute; left: {bar_width + 5}px; top: 0; font-size: 12px;'>{percent:.1f}%</div>"
        f"</div>"
    )
    return html

filtered_data["Views %"] = filtered_data["Views %"].apply(bar_html)

# Insert Views % chart column right after Views column, with no header
filtered_data[""] = filtered_data["Views %"]  # Empty string as column name

# Select columns to show, placing Views % chart right after Views
show_cols = [
    "Rank", "Preview", "App name", "Avatar", "Owner", "URL", "Views", "", "GitHub", "Views (past 30 days)"
]

st.subheader("App Ranking Table with Views % Bar Chart")
st.write(
    filtered_data[show_cols].to_html(escape=False, index=False, classes="my-table"),
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        .my-table, .my-table th, .my-table td {
            font-size: 11px !important;
        }
        .my-table th {
            text-align: left !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Metrics section
total_apps = len(filtered_data)
total_views = filtered_data["Views_num"].sum()
max_views = filtered_data["Views_num"].max()
avg_views = filtered_data["Views_num"].mean()

st.subheader("📈 Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Apps", total_apps)
col2.metric("Total Views", f"{int(total_views):,}")
col3.metric("Max Views", f"{int(max_views):,}")
col4.metric("Avg Views", f"{int(avg_views):,}")

# Add custom grey background color style for the app
st.markdown(
    """
    <style>
        body, .main {
            background-color: #e0e0e0;
        }
        table {
            background-color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True
)