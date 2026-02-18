import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
WORKSHEET_NAME = "Sheet2"


def connect():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


@st.cache_data(ttl=60)
def load_sheet():
    sheet = connect()
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    data = worksheet.get_all_records()

    if not data:
        return pd.DataFrame(columns=["Document Number", "Sl No", "Status"])

    return pd.DataFrame(data)


def ensure_columns():
    sheet = connect()
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    headers = worksheet.row_values(1)
    required = ["Document Number", "Sl No", "Status"]

    if not headers:
        worksheet.append_row(required)
        return

    for col in required:
        if col not in headers:
            headers.append(col)

    worksheet.update("A1", [headers])


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

    worksheet.append_row([document_number, slno, new_status])

