import streamlit as st
import pandas as pd
from sheets import load_sheet

# -----------------------------------
# USER PASSWORDS
# -----------------------------------
USERS = {
    "planning": "KDT@78",
    "operations": "KDT@98"
}

# -----------------------------------
# SESSION STATE INIT
# -----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None


# -----------------------------------
# LOGIN FUNCTION
# -----------------------------------
def login():

    st.set_page_config(
        page_title="Pending Order ERP",
        layout="centered"
    )

    st.title("🔐 Login")

    role = st.selectbox("Select User Type", ["planning", "operations"])
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):

        if password == USERS[role]:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Invalid Password")


# -----------------------------------
# SHOW LOGIN IF NOT LOGGED IN
# -----------------------------------
if not st.session_state.logged_in:
    login()
    st.stop()


# -----------------------------------
# MAIN APP STARTS HERE
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
# Sidebar
# -----------------------------------
st.sidebar.title("Options")
st.sidebar.success(f"Logged in as: {st.session_state.role}")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
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
# Snapshot Function
# -----------------------------------
def show_snapshot(final_df):

    if final_df.empty:
        st.warning("No record found.")
        return

    row = final_df.iloc[0]

    st.markdown("## 📋 Order Snapshot")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Party Name**")
        st.write(row.get("Party Name", "-"))

        st.markdown("**Part Name**")
        st.write(row.get("Part Name", "-"))

        st.markdown("**Material Grade**")
        st.write(row.get("Material Grade", "-"))

        st.markdown("**HT Priority**")
        st.write(row.get("HT Priority", "-"))

        st.markdown("**HT Detail**")
        st.write(row.get("HT Detail", "-"))

    with col2:
        st.markdown("**Order Qty**")
        st.write(row.get("Order Qty", "-"))

        st.markdown("**Pending Qty**")
        st.write(row.get("Pending Qty", "-"))

        st.markdown("**TPI Agency**")
        st.write(row.get("TPI Agency", "-"))

        st.markdown("**CutWt**")
        st.write(row.get("CutWt", "-"))


# -----------------------------------
# Search Type Selection
# -----------------------------------
search_type = st.radio(
    "Search By",
    ["Party Name", "Document Number"]
)

# ============================================================
# SEARCH BY PARTY NAME
# ============================================================
if search_type == "Party Name":

    party_list = sorted(df["Party Name"].dropna().unique())
    selected_party = st.selectbox("Select Party Name", party_list)

    party_df = df[df["Party Name"] == selected_party]

    if not party_df.empty:

        st.markdown("### 📄 Available Pending Orders")
        st.dataframe(
            party_df[["Document Number", "SLNo"]].drop_duplicates(),
            use_container_width=True
        )

        doc_list = sorted(party_df["Document Number"].dropna().unique())
        selected_doc = st.selectbox("Select Document Number", doc_list)

        doc_df = party_df[party_df["Document Number"] == selected_doc]

        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        show_snapshot(final_df)

# ============================================================
# SEARCH BY DOCUMENT NUMBER
# ============================================================
elif search_type == "Document Number":

    doc_list = sorted(df["Document Number"].dropna().unique())
    selected_doc = st.selectbox("Select Document Number", doc_list)

    doc_df = df[df["Document Number"] == selected_doc]

    if not doc_df.empty:

        st.markdown("### 👤 Party Name")
        st.success(doc_df["Party Name"].iloc[0])

        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        show_snapshot(final_df)
