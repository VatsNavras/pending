@st.cache_data
def load_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key("Pending Dashboard")
    ws = sheet.worksheet("Sheet1")

    data = ws.get_all_records()
    return pd.DataFrame(data)
