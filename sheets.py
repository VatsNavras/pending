import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1rwNOj7LzIykH3l2LW_3Ohz6IxUXT8C7ES3D5v3FRfaE"
WORKSHEET_NAME = "Sheet1"


@st.cache_data
def load_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.worksheet(WORKSHEET_NAME)

    data = worksheet.get_all_records()

    return pd.DataFrame(data)
