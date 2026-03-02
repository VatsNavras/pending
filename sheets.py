import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# ===================================
# CONNECT TO GOOGLE SHEET
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

    return client.open_by_key(st.secrets["1xCFURsxL3xv6zeN9ElYMPaE_A5sBOZewOZAH1cWdT0A"])


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
            rows="2000",
            cols="10"
        )
        worksheet.append_row(
            ["Document Number", "SLNo", "Status", "Updated By", "Last Updated On"]
        )

    records = worksheet.get_all_records()

    status_dict = {
        (str(row["Document Number"]), str(row["SLNo"])): {
            "status": row.get("Status", "Pending"),
            "updated_by": row.get("Updated By", ""),
            "timestamp": row.get("Last Updated On", "")
        }
        for row in records
    }

    return worksheet, records, status_dict


# ===================================
# GET CURRENT STATUS + TIMESTAMP
# ===================================
def get_status(document_number, slno):

    _, _, status_dict = load_status_sheet()

    data = status_dict.get(
        (str(document_number), str(slno)),
        None
    )

    if data:
        return data["status"], data["updated_by"], data["timestamp"]

    return "No Planned", "-", "-"


# ===================================
# UPDATE STATUS WITH TIMESTAMP
# ===================================
def update_status_in_sheet(document, slno, status, updated_by):

    worksheet, records, _ = load_status_sheet()

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    for i, row in enumerate(records, start=2):
        if (
            str(row.get("Document Number")) == str(document)
            and str(row.get("SLNo")) == str(slno)
        ):
            worksheet.update(
                f"C{i}:E{i}",
                [[status, updated_by, timestamp]]
            )
            load_status_sheet.clear()
            return

    worksheet.append_row(
        [document, slno, status, updated_by, timestamp]
    )

    load_status_sheet.clear()
