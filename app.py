import streamlit as st
import pandas as pd
from sheets import load_sheet

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Pending Order ERP",
    layout="centered"
)

# -----------------------------------
# Sidebar Refresh Button
# -----------------------------------
st.sidebar.title("Options")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------------
# Main Title
# -----------------------------------
st.title("📦 Pending Order Lookup")

# -----------------------------------
# Load Data
# -----------------------------------
df = load_sheet()

if df.empty:
    st.warning("No data found in Google Sheet.")
    st.stop()

# Clean column names (removes hidden spaces)
df.columns = df.columns.str.strip()

# -----------------------------------
# 1️⃣ Party Name Dropdown
# -----------------------------------
if "Party Name" not in df.columns:
    st.error("Column 'Party Name' not found in sheet.")
    st.write("Available columns:", df.columns)
    st.stop()

parties = sorted(df["Party Name"].astype(str).unique())

party = st.selectbox(
    "Select Party Name",
    parties
)

# Filter by Party Name
party_df = df[df["Party Name"].astype(str) == party]

# -----------------------------------
# 2️⃣ Document Number Dropdown
# -----------------------------------
if "Document Number" not in party_df.columns:
    st.error("Column 'Document Number' not found.")
    st.stop()

doc_numbers = sorted(party_df["Document Number"].astype(str).unique())

doc = st.selectbox(
    "Select Document Number",
    doc_numbers
)

# Filter by document
doc_df = party_df[
    party_df["Document Number"].astype(str) == doc
]

# -----------------------------------
# 3️⃣ SLNo Dropdown
# -----------------------------------
if "SLNo" not in doc_df.columns:
    st.error("Column 'SLNo' not found.")
    st.stop()

sl_options = sorted(doc_df["SLNo"].astype(str).unique())

sl_no = st.selectbox(
    "Select SL No",
    sl_options
)

# -----------------------------------
# Get Selected Row
# -----------------------------------
selected_row = doc_df[
    doc_df["SLNo"].astype(str) == sl_no
]

if selected_row.empty:
    st.warning("No matching record found.")
    st.stop()

row = selected_row.iloc[0]

st.divider()

# -----------------------------------
# Professional Layout
# -----------------------------------
st.markdown("### 📋 Order Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Party Name**")
    st.write(row.get("Party Name") or "-")

    st.markdown("**Part Name**")
    st.write(row.get("Part Name") or "-")

    st.markdown("**HT Detail**")
    st.write(row.get("HT Detail") or "-")

    st.markdown("**HT Priority**")
    st.write(row.get("HT Priority") or "-")

with col2:
    st.markdown("**Order Qty**")
    st.write(row.get("Order Qty") or "-")

    st.markdown("**Pending Qty**")
    st.write(row.get("Pending Qty") or "-")

    st.markdown("**TPI Agency**")
    st.write(row.get("TPI Agency") or "-")


