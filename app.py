import streamlit as st
import pandas as pd
from sheets import load_sheet

st.set_page_config(
    page_title="Pending Order ERP",
    layout="centered"
)

st.title("📦 Pending Order Lookup")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()


# -----------------------------
# Load Data
# -----------------------------
df = load_sheet()

if df.empty:
    st.warning("No data found.")
    st.stop()

# -----------------------------
# Document Number Dropdown
# -----------------------------
doc_numbers = sorted(df["Document Number"].astype(str).unique())

doc = st.selectbox(
    "Select Document Number",
    doc_numbers
)

# Filter based on Document
filtered_df = df[df["Document Number"].astype(str) == doc]

# -----------------------------
# SLNo Dropdown
# -----------------------------
sl_options = filtered_df["SLNo"].astype(str).unique()

sl_no = st.selectbox(
    "Select SL No",
    sl_options
)

# Final selected row
row = filtered_df[filtered_df["SLNo"].astype(str) == sl_no].iloc[0]

st.divider()

# -----------------------------
# Professional Card Layout
# -----------------------------
st.markdown("### 📋 Order Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Party Name**")
    st.write(row.get("Party Name", "-"))

    st.markdown("**Part Name**")
    st.write(row.get("Part Name", "-"))

    st.markdown("**HT Detail**")
    st.write(row.get("HT Detail", "-"))

    st.markdown("**HT Priority**")
    st.write(row.get("HT Priority", "-"))

with col2:
    st.markdown("**Order Qty**")
    st.write(row.get("Order Qty", "-"))

    st.markdown("**Pending Qty**")
    st.write(row.get("Pending Qty", "-"))

    st.markdown("**TPI Agency**")
    st.write(row.get("TPI Agency", "-"))

