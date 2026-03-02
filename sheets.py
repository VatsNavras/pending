import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime


SPREADSHEET_NAME = "pending_development"
DATA_SHEET = "Sheet1"
STATUS_SHEET = "Sheet2"


# -------------------------------
# CONNECTION
# -------------------------------
@st.cache_resource
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
    return client.open(SPREADSHEET_NAME)


# -------------------------------
# LOAD MAIN DATA (Sheet1)
# -------------------------------
@st.cache_data
def load_sheet():
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(DATA_SHEET)

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    return df


# -------------------------------
# GET STATUS FROM Sheet2
# -------------------------------
def get_status(document, slno):
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(STATUS_SHEET)

    records = sheet.get_all_records()

    for row in records:
        if str(row.get("Document Number")) == str(document) and str(row.get("SLNo")) == str(slno):
            return (
                row.get("Status"),
                row.get("Updated By"),
                row.get("Timestamp")
            )

    return ("Not Updated", "-", "-")


# -------------------------------
# UPDATE STATUS IN Sheet2
# -------------------------------
def update_status_in_sheet(document, slno, status, updated_by):
    spreadsheet = connect_to_spreadsheet()
    sheet = spreadsheet.worksheet(STATUS_SHEET)

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")

    records = sheet.get_all_records()

    # Check if entry exists
    for idx, row in enumerate(records, start=2):  # start=2 because row1 is header
        if str(row.get("Document Number")) == str(document) and str(row.get("SLNo")) == str(slno):

            sheet.update(f"C{idx}", status)
            sheet.update(f"D{idx}", updated_by)
            sheet.update(f"E{idx}", timestamp)
            return

    # If not found → append new row
    sheet.append_row([
        document,
        slno,
        status,
        updated_by,
        timestamp
    ])
