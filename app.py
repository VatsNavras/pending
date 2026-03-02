import streamlit as st
import pandas as pd
from sheets import load_sheet, update_status_in_sheet, get_status

# -----------------------------------
# USER DATABASE (TEMP)
# -----------------------------------
USERS = {
    "viewer1": {"password": "1234", "role": "viewer"},
    "planner1": {"password": "1234", "role": "planning"}
}

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="Pending Order ERP", layout="centered")

# -----------------------------------
# LOGIN SYSTEM
# -----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.error("Invalid Username or Password")

if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------------
# HEADER
# -----------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Logo.jpg", width=250)

st.markdown("<h2 style='text-align: center;'>Pending Order ERP System</h2>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------------
# LOAD DATA
# -----------------------------------
df = load_sheet()

if df.empty:
    st.warning("No data found.")
    st.stop()

df.columns = df.columns.str.strip()

# -----------------------------------
# SNAPSHOT FUNCTION
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
        st.write("**Party Name:**", row.get("Party Name", "-"))
        st.write("**Part Name:**", row.get("Part Name", "-"))
        st.write("**Material Grade:**", row.get("Material Grade", "-"))
        st.write("**HT Priority:**", row.get("HT Priority", "-"))
        st.write("**HT Detail:**", row.get("HT Detail", "-"))

    with col2:
        st.write("**Order Qty:**", row.get("Order Qty", "-"))
        st.write("**Pending Qty:**", row.get("Pending Qty", "-"))
        st.write("**TPI Agency:**", row.get("TPI Agency", "-"))
        st.write("**CutWt:**", row.get("CutWt", "-"))

    st.markdown("---")

    # STATUS + TIMESTAMP
    current_status, updated_by, timestamp = get_status(
        row["Document Number"],
        row["SLNo"]
    )

    st.write("### Current Status:", current_status)
    st.write("Last Updated By:", updated_by)
    st.write("Last Updated On:", timestamp)

    # -----------------------------------
    # PLANNING UPDATE SECTION
    # -----------------------------------
    if st.session_state.role == "planning":

        st.markdown("### ✏ Update Status")

        document_number = str(row["Document Number"])
        doc_df = df[df["Document Number"] == row["Document Number"]]

        select_all = st.checkbox("✅ Select All SLNo")

        selected_slnos = []

        for index, r in doc_df.iterrows():

            slno = str(r["SLNo"])
            status_now, _, _ = get_status(document_number, slno)

            if select_all:
                selected = True
            else:
                selected = st.checkbox(
                    f"SLNo: {slno} | Current Status: {status_now}",
                    key=f"chk_{slno}"
                )

            if selected:
                selected_slnos.append(slno)

        new_status = st.selectbox(
            "Select New Status",
            [
                "No Planned",
                "Under RM Procurement",
                "Under Forging",
                "Under Machining",
                "Under TPM",
                "Under HT",
                "Under NDT/DT",
                "Under Final Inspection",
                "Dispatched"
            ]
        )

        if st.button("🚀 Update Selected"):

            if not selected_slnos:
                st.warning("Please select at least one SLNo")
                return

            for slno in selected_slnos:
                update_status_in_sheet(
                    document=document_number,
                    slno=slno,
                    status=new_status,
                    updated_by=st.session_state.username
                )

            st.success("Status Updated Successfully")
            st.cache_data.clear()
            st.rerun()


# -----------------------------------
# SEARCH SECTION (UNCHANGED)
# -----------------------------------
search_type = st.radio("Search By", ["Party Name", "Document Number"])

if search_type == "Party Name":

    party_list = sorted(df["Party Name"].dropna().unique())
    selected_party = st.selectbox("Select Party Name", party_list)

    party_df = df[df["Party Name"] == selected_party]

    if not party_df.empty:

        doc_list = sorted(party_df["Document Number"].dropna().unique())
        selected_doc = st.selectbox("Select Document Number", doc_list)

        doc_df = party_df[party_df["Document Number"] == selected_doc]

        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        show_snapshot(final_df)

else:

    doc_list = sorted(df["Document Number"].dropna().unique())
    selected_doc = st.selectbox("Select Document Number", doc_list)

    doc_df = df[df["Document Number"] == selected_doc]

    if not doc_df.empty:

        st.success(doc_df["Party Name"].iloc[0])

        slno_list = sorted(doc_df["SLNo"].dropna().unique())
        selected_slno = st.selectbox("Select SLNo", slno_list)

        final_df = doc_df[doc_df["SLNo"] == selected_slno]

        show_snapshot(final_df)

