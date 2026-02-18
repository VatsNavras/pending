import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ===============================
# CONFIG
# ===============================
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
WORKSHEET_NAME = "Sheet2"

# ===============================
# CONNECT TO GOOGLE SHEET
# ===============================
def connect():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


# ===============================
# LOAD SHEET (CACHED)
# ===============================
@st.cache_data(ttl=60)
def load_sheet():
    sheet = connect()
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    data = worksheet.get_all_records()

    if not data:
        return pd.DataFrame(columns=["Document Number", "Sl No", "Status"])

    return pd.DataFrame(data)


# ===============================
# ENSURE COLUMNS EXIST
# ===============================
def ensure_columns():
    sheet = connect()
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    headers = worksheet.row_values(1)

    required_cols = ["Document Number", "Sl No", "Status"]

    if not headers:
        worksheet.append_row(required_cols)
        return

    for col in required_cols:
        if col not in headers:
            headers.append(col)

    worksheet.update("A1", [headers])


# ===============================
# UPDATE STATUS
# ===============================
def update_status(document_number, slno, new_status):
    sheet = connect()
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    records = worksheet.get_all_records()

    for i, row in enumerate(records, start=2):
        if (
            str(row.get("Document Number")) == str(document_number)
            and str(row.get("Sl No")) == str(slno)
        ):
            col_index = worksheet.row_values(1).index("Status") + 1
            worksheet.update_cell(i, col_index, new_status)
            return

    # If not found, append new row
    worksheet.append_row([document_number, slno, new_status])



