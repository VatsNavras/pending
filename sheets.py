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
    Stable Google Sheets connection for Streamlit Cloud
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

    status_dict = {}

    for row in records:
        doc = str(row.get("Document Number"))
        sl = str(row.get("SLNo"))

        status_dict[(doc, sl)] = {
            "status": row.get("Status", "Pending"),
            "updated_by": row.get("Updated By", ""),
            "timestamp": row.get("Last Updated On", "")
        }

    return worksheet, records, status_dict


# ===================================
# GET CURRENT STATUS
# ===================================
def get_status(document_number, slno):

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

    worksheet, records, _ = load_status_sheet()

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Search existing entry
    for index, row in enumerate(records, start=2):  # row 1 is header
        if (
            str(row.get("Document Number")) == str(document)
            and str(row.get("SLNo")) == str(slno)
        ):

            worksheet.update(
                range_name=f"C{index}:E{index}",
                values=[[status, updated_by, timestamp]]
            )

            load_status_sheet.clear()
            return

    # If not found → append new
    worksheet.append_row(
        [document, slno, status, updated_by, timestamp]
    )

    load_status_sheet.clear()
