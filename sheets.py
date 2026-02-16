import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SPREADSHEET_NAME = "Pending Dashboard"
WORKSHEET_NAME = "Sheet1"

@st.cache_data
def load_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet = client.open("Pending Dashboard")
    ws = sheet.worksheet("Sheet1")

    data = ws.get_all_records()
    return pd.DataFrame(data)
