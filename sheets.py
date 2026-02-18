import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1xCFURsxL3xv6zeN9ElYMPaE_A5sBOZewOZAH1cWdT0A"
WORKSHEET_NAME = "Sheet1"


# -----------------------------------
# CONNECT TO GOOGLE SHEET (READ + WRITE)
# -----------------------------------
def connect_to_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    return worksheet


# -----------------------------------
# LOAD DATA (CACHED)
# -----------------------------------
@st.cache_data(ttl=30)
def load_sheet():

    worksheet = connect_to_sheet()
    data = worksheet.get_all_records()

    return pd.DataFrame(data)


# -----------------------------------
# UPDATE STATUS FUNCTION
# -----------------------------------
def update_status_in_sheet(document, slno, status, updated_by, timestamp):

    worksheet = connect_to_sheet()
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Find matching row
    row_index = df[
        (df["Document Number"] == document) &
        (df["SLNo"] == slno)
    ].index

    if not row_index.empty:

        sheet_row_number = row_index[0] + 2  # +2 because sheet starts at row 2

        worksheet.update_cell(
            sheet_row_number,
            df.columns.get_loc("Status") + 1,
            status
        )

        worksheet.update_cell(
            sheet_row_number,
            df.columns.get_loc("Updated By") + 1,
            updated_by
        )

        worksheet.update_cell(
            sheet_row_number,
            df.columns.get_loc("Last Updated") + 1,
            timestamp
        )
