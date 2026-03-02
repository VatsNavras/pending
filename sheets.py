import streamlit as st
import gspread
import pandas as pd
from datetime import datetime


# ===================================
# CONNECT TO GOOGLE SHEET
# ===================================
@st.cache_resource
def connect():
    """
    Connect to Google Sheet using Streamlit secrets.
    Uses gspread native authentication (Cloud-safe).
    """
    client = gspread.service_account_from_dict(
        st.secrets["gcp_service_account"]
    )

    return client.open_by_key(st.secrets["SPREADSHEET_ID"])


# ===================================
# LOAD MAIN ERP DATA (Sheet1)
# ===================================
@st.cache_data(ttl=60)
def load_sheet():
    """
    Load main data from Sheet1.
    """
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
    """
    Load or create Sheet2 for status tracking.
    Returns:
        worksheet object,
        list of records,
        dictionary for quick lookup
    """
    spreadsheet = connect()

    try:
        worksheet = spreadsheet.worksheet("Sheet2")
    except gspread.exceptions.WorksheetNotFound:
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
        (str(row.get("Document Number")), str(row.get("SLNo"))): {
            "status": row.get("Status", "Pending"),
            "updated_by": row.get("Updated By", ""),
            "timestamp": row.get("Last Updated On", "")
        }
        for row in records
    }

    return worksheet, records, status_dict


# ===================================
# GET CURRENT STATUS
# ===================================
def get_status(document_number, slno):
    """
    Fetch current status for given Document + SLNo.
    """
    _, _, status_dict = load_status_sheet()

    data = status_dict.get(
        (str(document_number), str(slno))
    )

    if data:
        return data["status"], data["updated_by"], data["timestamp"]

    return "No Planned", "-", "-"


# ===================================
# UPDATE STATUS WITH TIMESTAMP
# ===================================
def update_status_in_sheet(document, slno, status, updated_by):
    """
    Update existing row if found,
    else append new row.
    """
    worksheet, records, _ = load_status_sheet()

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Check if entry exists
    for i, row in enumerate(records, start=2):  # Start at row 2 (header row is 1)
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

    # If not found → append new row
    worksheet.append_row(
        [document, slno, status, updated_by, timestamp]
    )

    load_status_sheet.clear()
