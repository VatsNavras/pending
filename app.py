import streamlit as st
import pandas as pd
from sheets import load_sheet

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(
    page_title="Pending Order ERP",
    layout="centered"
)

# -----------------------------------
# Centered Logo
# -----------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Logo.jpg", width=250)

st.markdown("<h2 style='text-align: center;'>Pending Order ERP System</h2>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------
# Sidebar Refresh
# -----------------------------------
st.sidebar.title("Options")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------------
# Load Data
# -----------------------------------
df = load_sheet()

if df.empty:
    st.warning("No data found in Google Sheet.")
    st.stop()

df.columns = df.columns.str.strip()

required_cols = ["Party Name", "Document Number", "SLNo"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Column '{col}' not found in sheet.")
        st.stop()

# -----------------------------------
# Search Type Selection
# -----------------------------------
search_type = st.radio(
    "Search By",
    ["Party Name", "Document Number"]
)

# ============================================================
# 🔵 SEARCH BY PARTY NAME
# ============================================================
if search_type == "Party Name":

    party_list = sorted(df["Party Name"].dropna().unique())
    selected_party = st.selectbox("Select Party Name", party_list)

    # Filter by Party
    party_df = df[df["Party Name"] == selected_party]

    if not party_df.empty:

        st.markdown("### 📄 All Documents for this Party")
        st.dataframe(
            party_df[["Document Number", "SLNo"]].drop_duplicates(),
            use_container_width=True
        )

        # Select Document
        doc_list = sorted(party_df["Document Number"].dropna().unique())
        selected_doc = st.selectbox("Select Document Number", doc_list)

        doc_df = party_df[party_df["Document Number"] == selected_doc]

        # Select SLNo
        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        st.markdown("### 📄 Document Details")
        st.dataframe(final_df, use_container_width=True)

# ============================================================
# 🔴 SEARCH BY DOCUMENT NUMBER
# ============================================================
elif search_type == "Document Number":

    doc_list = sorted(df["Document Number"].dropna().unique())
    selected_doc = st.selectbox("Select Document Number", doc_list)

    doc_df = df[df["Document Number"] == selected_doc]

    if not doc_df.empty:

        st.markdown("### 👤 Party Name")
        st.success(doc_df["Party Name"].iloc[0])

        # Show all SLNo for this document
        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        st.markdown("### 📄 Document Details")
        st.dataframe(final_df, use_container_width=True)
