import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------
# CONFIG
# -----------------------------------
SPREADSHEET_ID = "PASTE_YOUR_SPREADSHEET_ID_HERE"


# -----------------------------------
# CONNECT TO GOOGLE SHEETS
# -----------------------------------
def get_worksheet():
    creds_dict = dict(st.secrets["gcp_service_account"])

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet


# -----------------------------------
# LOAD SHEET
# -----------------------------------
@st.cache_data(ttl=60)
def load_sheet():
    sheet = get_worksheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)


# -----------------------------------
# SAFE COLUMN FINDER
# -----------------------------------
def find_column(headers, target_name):
    for i, col in enumerate(headers):
        if col.strip().lower() == target_name.strip().lower():
            return i + 1
    return None


# -----------------------------------
# GET STATUS
# -----------------------------------
def get_status(document, slno):
    sheet = get_worksheet()
    records = sheet.get_all_records()

    for row in records:
        if str(row.get("Document Number")) == str(document) and str(row.get("SLNo")) == str(slno):
            return (
                row.get("Status", "No Planned"),
                row.get("Updated By", "-"),
                row.get("Timestamp", "-"),
            )

    return "No Planned", "-", "-"


# -----------------------------------
# UPDATE STATUS (FULLY SAFE)
# -----------------------------------
def update_status_in_sheet(document, slno, status, updated_by):

    sheet = get_worksheet()
    records = sheet.get_all_records()
    headers = sheet.row_values(1)

    # Auto-create missing columns
    required_columns = ["Status", "Updated By", "Timestamp"]

    for col_name in required_columns:
        if not any(h.strip().lower() == col_name.lower() for h in headers):
            sheet.update_cell(1, len(headers) + 1, col_name)
            headers = sheet.row_values(1)

    # Find columns safely
    status_col = find_column(headers, "Status")
    updated_by_col = find_column(headers, "Updated By")
    timestamp_col = find_column(headers, "Timestamp")

    if not status_col or not updated_by_col or not timestamp_col:
        st.error("Required columns missing in sheet.")
        return

    for index, row in enumerate(records):
        if str(row.get("Document Number")) == str(document) and str(row.get("SLNo")) == str(slno):

            excel_row = index + 2  # +2 for header offset

            sheet.update_cell(excel_row, status_col, status)
            sheet.update_cell(excel_row, updated_by_col, updated_by)
            sheet.update_cell(
                excel_row,
                timestamp_col,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            break
