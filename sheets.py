import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# -----------------------------------
# CONNECT TO GOOGLE SHEET
# -----------------------------------
def connect():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(st.secrets["SPREADSHEET_ID"])

    return spreadsheet


# -----------------------------------
# LOAD MAIN ERP DATA (Sheet1)
# -----------------------------------
@st.cache_data(ttl=60)
def load_sheet():

    spreadsheet = connect()

    worksheet = spreadsheet.worksheet("Sheet1")

    data = worksheet.get_all_records()

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)


# -----------------------------------
# GET OR CREATE STATUS SHEET (Sheet2)
# -----------------------------------
def get_status_sheet():

    spreadsheet = connect()

    try:
        worksheet = spreadsheet.worksheet("Sheet2")
    except:
        worksheet = spreadsheet.add_worksheet(
            title="Sheet2",
            rows="1000",
            cols="10"
        )

        worksheet.append_row(
            ["Document Number", "SLNo", "Status", "Updated By"]
        )

    return worksheet


# -----------------------------------
# GET CURRENT STATUS
# -----------------------------------
def get_status(document_number, slno):

    sheet = get_status_sheet()

    records = sheet.get_all_records()

    for row in records:
        if (
            str(row.get("Document Number")) == str(document_number)
            and str(row.get("SLNo")) == str(slno)
        ):
            return row.get("Status", "Pending")

    return "Pending"


# -----------------------------------
# UPDATE STATUS
# -----------------------------------
def update_status_in_sheet(document, slno, status, updated_by):

    sheet = get_status_sheet()

    records = sheet.get_all_records()

    # Check if already exists → update
    for i, row in enumerate(records, start=2):
        if (
            str(row.get("Document Number")) == str(document)
            and str(row.get("SLNo")) == str(slno)
        ):
            sheet.update_cell(i, 3, status)       # Status column
            sheet.update_cell(i, 4, updated_by)   # Updated By column
            return

    # If not found → append new row
    sheet.append_row([document, slno, status, updated_by])


