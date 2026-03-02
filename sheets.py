import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ===================================
# CONNECT TO GOOGLE SHEET (ONCE)
# ===================================
@st.cache_resource
def connect():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    return client.open_by_key(st.secrets["SPREADSHEET_ID"])


# ===================================
# LOAD MAIN ERP DATA (Sheet1)
# ===================================
@st.cache_data(ttl=60)
def load_sheet():

    spreadsheet = connect()
    worksheet = spreadsheet.worksheet("Sheet1")

    data = worksheet.get_all_records()

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)


# ===================================
# LOAD STATUS SHEET (Sheet2)
# ===================================
@st.cache_data(ttl=60)
def load_status_sheet():

    spreadsheet = connect()

    try:
        worksheet = spreadsheet.worksheet("Sheet2")
    except:
        worksheet = spreadsheet.add_worksheet(
            title="Sheet2",
            rows="1000",
            cols="10"
        )
        worksheet.append_row(
            ["Document Number", "SLNo", "Status", "Updated By"]
        )

    records = worksheet.get_all_records()

    # Convert to dictionary for O(1) lookup
    status_dict = {
        (str(row["Document Number"]), str(row["SLNo"])): row["Status"]
        for row in records
    }

    return worksheet, records, status_dict


# ===================================
# GET CURRENT STATUS (FAST LOOKUP)
# ===================================
def get_status(document_number, slno):

    _, _, status_dict = load_status_sheet()

    return status_dict.get(
        (str(document_number), str(slno)),
        "Pending"
    )


# ===================================
# UPDATE STATUS
# ===================================
def update_status_in_sheet(document, slno, status, updated_by):

    worksheet, records, _ = load_status_sheet()

    # Check if exists → update
    for i, row in enumerate(records, start=2):
        if (
            str(row.get("Document Number")) == str(document)
            and str(row.get("SLNo")) == str(slno)
        ):
            worksheet.update(f"C{i}:D{i}", [[status, updated_by]])
            load_status_sheet.clear()
            return

    # If not found → append
    worksheet.append_row([document, slno, status, updated_by])

    load_status_sheet.clear()

