import gspread
from google.oauth2.service_account import Credentials
import streamlit as st


# ----------------------------
# CONNECT TO GOOGLE SHEETS
# ----------------------------
def connect_sheet():

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


# ----------------------------
# GET OR CREATE SHEET2
# ----------------------------
def get_sheet2():

    spreadsheet = connect_sheet()

    try:
        worksheet = spreadsheet.worksheet("Sheet2")
    except:
        # Create Sheet2 if not exists
        worksheet = spreadsheet.add_worksheet(
            title="Sheet2",
            rows="1000",
            cols="20"
        )

    return worksheet


# ----------------------------
# ENSURE HEADERS EXIST
# ----------------------------
def ensure_headers():

    sheet = get_sheet2()

    expected_headers = ["Date", "Name", "Amount", "Status"]

    current_headers = sheet.row_values(1)

    if current_headers != expected_headers:
        sheet.update("A1:D1", [expected_headers])


# ----------------------------
# ADD ENTRY TO SHEET2
# ----------------------------
def add_entry(date, name, amount, status):

    ensure_headers()

    sheet = get_sheet2()

    sheet.append_row([date, name, amount, status])


# ----------------------------
# GET ALL DATA FROM SHEET2
# ----------------------------
def get_all_data():

    sheet = get_sheet2()

    return sheet.get_all_records()

