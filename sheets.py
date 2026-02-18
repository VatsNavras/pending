import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime


# ==============================
# CONFIG
# ==============================
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
MAIN_SHEET = "Sheet1"
STATUS_SHEET = "Sheet2"


# ==============================
# CONNECT TO GOOGLE SHEET
# ==============================
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


# ==============================
# LOAD MAIN DATA (Sheet1)
# ==============================
@st.cache_data(ttl=30)
def load_sheet():

    sheet = connect()
    worksheet = sheet.worksheet(MAIN_SHEET)

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        df.columns = df.columns.str.strip()

    return df


# ==============================
# GET OR CREATE STATUS SHEET (Sheet2)
# ==============================
def get_status_sheet():

    sheet = connect()

    try:
        worksheet = sheet.worksheet(STATUS_SHEET)
    except:
        worksheet = sheet.add_worksheet(
            title=STATUS_SHEET,
            rows="1000",
            cols="10"
        )

        # Create header automatically
        worksheet.append_row([
            "Document Number",
            "SLNo",
            "Status",
            "Updated By",
            "Last Updated"
        ])

    return worksheet


# ==============================
# UPDATE STATUS (WRITE TO SHEET2)
# ==============================
def update_status_in_sheet(document, slno, status, updated_by):

    worksheet = get_status_sheet()

    # Convert everything to string (prevents JSON error)
    document = str(document)
    slno = str(slno)
    status = str(status)
    updated_by = str(updated_by)
    timestamp = str(datetime.now())

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # If sheet empty → insert first row
    if df.empty:
        worksheet.append_row(
            [document, slno, status, updated_by, timestamp]
        )
        return

    # Clean column names
    df.columns = df.columns.str.strip()

    # Ensure comparison works
    df["Document Number"] = df["Document Number"].astype(str)
    df["SLNo"] = df["SLNo"].astype(str)

    match = df[
        (df["Document Number"] == document) &
        (df["SLNo"] == slno)
    ]

    if not match.empty:
        row_number = match.index[0] + 2  # +2 because header row exists

        worksheet.update(
            f"A{row_number}:E{row_number}",
            [[document, slno, status, updated_by, timestamp]]
        )
    else:
        worksheet.append_row(
            [document, slno, status, updated_by, timestamp]
        )


# ==============================
# GET STATUS FOR DISPLAY
# ==============================
def get_status(document, slno):

    worksheet = get_status_sheet()

    document = str(document)
    slno = str(slno)

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        return "Not Updated"

    df.columns = df.columns.str.strip()

    df["Document Number"] = df["Document Number"].astype(str)
    df["SLNo"] = df["SLNo"].astype(str)

    match = df[
        (df["Document Number"] == document) &
        (df["SLNo"] == slno)
    ]

    if not match.empty:
        return match.iloc[0]["Status"]

    return "Not Updated"


