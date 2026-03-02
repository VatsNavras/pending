import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd


# ----------------------------
# CONNECT TO GOOGLE SHEET
# ----------------------------
def get_worksheet(sheet_name):
    creds_dict = dict(st.secrets["gcp_service_account"])

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.sheet1

    return worksheet


# ----------------------------
# LOAD SHEET (Old Name Supported)
# ----------------------------
def load_sheet(sheet_name):
    worksheet = get_worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)


# ----------------------------
# GET STATUS (Optional Helper)
# ----------------------------
def get_status(sheet_name):
    worksheet = get_worksheet(sheet_name)
    return worksheet.get_all_records()


# ----------------------------
# UPDATE STATUS SAFELY
# ----------------------------
def update_status_in_sheet(sheet_name, row_number, status_column_number, new_status):
    worksheet = get_worksheet(sheet_name)
    worksheet.update_cell(row_number, status_column_number, new_status)
