import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_NAME = "pending_development"
DATA_SHEET = "Sheet1"
STATUS_SHEET = "Sheet2"


def connect_to_spreadsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)

    return spreadsheet


# ✅ Load main data (Sheet1)
def load_sheet():
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(DATA_SHEET)
    return sheet.get_all_records()


# ✅ Update status in Sheet2
def update_status_in_sheet(row_number, col_name, value):
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(STATUS_SHEET)

    headers = sheet.row_values(1)

    # Add column if not exists
    if col_name not in headers:
        headers.append(col_name)
        sheet.update('1:1', [headers])

    headers = sheet.row_values(1)
    col_index = headers.index(col_name) + 1

    sheet.update_cell(row_number, col_index, value)


# ✅ Get status from Sheet2
def get_status(row_number, col_name):
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(STATUS_SHEET)

    headers = sheet.row_values(1)

    if col_name not in headers:
        return None

    col_index = headers.index(col_name) + 1
    return sheet.cell(row_number, col_index).value
