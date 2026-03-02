import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_NAME = "pending_development"
STATUS_SHEET_NAME = "Sheet2"   # 👈 IMPORTANT


def connect_sheet(sheet_name):
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

    sheet = spreadsheet.worksheet(sheet_name)  # 👈 select specific sheet

    return sheet


def update_status_in_sheet(row_number, col_name, value):
    sheet = connect_sheet(STATUS_SHEET_NAME)

    headers = sheet.row_values(1)

    # Add column if not exists
    if col_name not in headers:
        headers.append(col_name)
        sheet.update('1:1', [headers])  # safer batch update

    # Refresh headers
    headers = sheet.row_values(1)
    col_index = headers.index(col_name) + 1

    # Update cell
    sheet.update_cell(row_number, col_index, value)
