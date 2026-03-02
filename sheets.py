import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
from datetime import datetime

SHEET_NAME = "Pending Orders"  # 👈 Put your exact Google Sheet name here


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
    sheet = client.open("pending_development").sheet1
    return sheet


# -----------------------------------
# LOAD FULL SHEET
# -----------------------------------
@st.cache_data(ttl=60)
def load_sheet():
    sheet = get_worksheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)


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
# UPDATE STATUS
# -----------------------------------
def update_status_in_sheet(document, slno, status, updated_by):
    sheet = get_worksheet()
    records = sheet.get_all_records()

    for index, row in enumerate(records):
        if str(row.get("Document Number")) == str(document) and str(row.get("SLNo")) == str(slno):

            # +2 because:
            # Row 1 = header
            # enumerate starts at 0
            excel_row = index + 2

            headers = sheet.row_values(1)

            status_col = headers.index("Status") + 1
            updated_by_col = headers.index("Updated By") + 1
            timestamp_col = headers.index("Timestamp") + 1

            sheet.update_cell(excel_row, status_col, status)
            sheet.update_cell(excel_row, updated_by_col, updated_by)
            sheet.update_cell(
                excel_row,
                timestamp_col,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            break
