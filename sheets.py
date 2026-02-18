import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
MAIN_SHEET = "Sheet1"
STATUS_SHEET = "Sheet2"

def connect():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )

    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

@st.cache_data(ttl=30)
def load_sheet():
    sheet = connect()
    worksheet = sheet.worksheet(MAIN_SHEET)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def get_status_sheet():
    sheet = connect()
    try:
        worksheet = sheet.worksheet(STATUS_SHEET)
    except:
        worksheet = sheet.add_worksheet(title=STATUS_SHEET, rows="1000", cols="10")
        worksheet.append_row([
            "Document Number",
            "SLNo",
            "Status",
            "Updated By",
            "Last Updated"
        ])
    return worksheet

def update_status_in_sheet(document, slno, status, updated_by):
    worksheet = get_status_sheet()
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    timestamp = str(datetime.now())

    if df.empty:
        worksheet.append_row([document, slno, status, updated_by, timestamp])
        return

    match = df[
        (df["Document Number"] == document) &
        (df["SLNo"] == slno)
    ]

    if not match.empty:
        row_number = match.index[0] + 2
        worksheet.update(f"A{row_number}:E{row_number}", [[
            document, slno, status, updated_by, timestamp
        ]])
    else:
        worksheet.append_row([document, slno, status, updated_by, timestamp])

def get_status(document, slno):
    worksheet = get_status_sheet()
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        return "Not Updated"

    match = df[
        (df["Document Number"] == document) &
        (df["SLNo"] == slno)
    ]

    if not match.empty:
        return match.iloc[0]["Status"]

    return "Not Updated"

