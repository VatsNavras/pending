import streamlit as st
import pandas as pd
from sheets import load_sheet, update_status, ensure_columns



st.set_page_config(page_title="Order Status App", layout="wide")

st.title("Order Status Management")

# Ensure required columns exist
ensure_columns()

# ===============================
# SEARCH SECTION (Same as before)
# ===============================
st.subheader("Search Order")

document_number = st.text_input("Enter Document Number")

if document_number:
    sheet_df = load_sheet()

    result_df = sheet_df[
        sheet_df["Document Number"].astype(str) == str(document_number)
    ]

    if result_df.empty:
        st.warning("No records found.")
    else:
        st.success("Order Found")

        st.dataframe(result_df)

        st.markdown("---")
        st.subheader("Update Status")

        # ===============================
        # UPDATE SECTION
        # ===============================

        update_all = st.checkbox("Update ALL rows")

        new_status = st.selectbox(
            "Select New Status",
            ["Pending", "In Progress", "Completed"]
        )

        if update_all:
            if st.button("Update All"):
                for _, row in result_df.iterrows():
                    update_status(
                        row["Document Number"],
                        row["Sl No"],
                        new_status
                    )

                st.cache_data.clear()
                st.success("All rows updated successfully!")

        else:
            selected_slno = st.selectbox(
                "Select Sl No",
                result_df["Sl No"]
            )

            if st.button("Update Selected"):
                update_status(
                    document_number,
                    selected_slno,
                    new_status
                )

                st.cache_data.clear()
                st.success("Selected row updated successfully!")




