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
# Title
# -----------------------------------
st.title("📦 Pending Order Lookup")

# -----------------------------------
# Load Data
# -----------------------------------
df = load_sheet()

if df.empty:
    st.warning("No data found in Google Sheet.")
    st.stop()

df.columns = df.columns.str.strip()

# Validate required columns
required_cols = ["Party Name", "Document Number", "SLNo"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Column '{col}' not found in sheet.")
        st.write("Available columns:", df.columns)
        st.stop()

# -----------------------------------
# 1️⃣ Search Type Selection
# -----------------------------------
search_type = st.selectbox(
    "Search By",
    ["Party Name", "Document Number"]
)

# -----------------------------------
# 2️⃣ Dynamic First Filter
# -----------------------------------
if search_type == "Party Name":
    options = sorted(df["Party Name"].astype(str).unique())
    selected_value = st.selectbox("Select Party Name", options)
    filtered_df = df[df["Party Name"].astype(str) == selected_value]

else:
    options = sorted(df["Document Number"].astype(str).unique())
    selected_value = st.selectbox("Select Document Number", options)
    filtered_df = df[df["Document Number"].astype(str) == selected_value]

# -----------------------------------
# 3️⃣ SLNo Dropdown
# -----------------------------------
sl_options = sorted(filtered_df["SLNo"].astype(str).unique())

sl_no = st.selectbox(
    "Select SL No",
    sl_options
)

selected_row = filtered_df[
    filtered_df["SLNo"].astype(str) == sl_no
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
    st.markdown("**Document Number**")
    st.write(row.get("Document Number") or "-")

    st.markdown("**Order Qty**")
    st.write(row.get("Order Qty") or "-")

    st.markdown("**Pending Qty**")
    st.write(row.get("Pending Qty") or "-")

    st.markdown("**TPI Agency**")
    st.write(row.get("TPI Agency") or "-")


