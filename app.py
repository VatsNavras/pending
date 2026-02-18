import streamlit as st
import pandas as pd
from sheets import load_sheet, update_status, ensure_columns

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Order Status Management",
    layout="wide"
)

st.title("📦 Order Status Management System")

# ==========================================
# ENSURE REQUIRED COLUMNS EXIST
# ==========================================
ensure_columns()

# ==========================================
# SEARCH SECTION (LIKE PREVIOUS VERSION)
# ==========================================
st.subheader("🔍 Search Order")

document_number = st.text_input("Enter Document Number")

if document_number:

    # Load Sheet Data
    sheet_df = load_sheet()

    # Filter by document number
    result_df = sheet_df[
        sheet_df["Document Number"].astype(str) == str(document_number)
    ]

    if result_df.empty:
        st.warning("No records found for this Document Number.")
    else:
        st.success("Order Found ✅")

        # Show results
        st.dataframe(result_df, use_container_width=True)

        st.markdown("---")
        st.subheader("🛠 Update Status")

        # ==========================================
        # UPDATE OPTIONS
        # ==========================================
        update_all = st.checkbox("Update ALL rows for this Document Number")

        new_status = st.selectbox(
            "Select New Status",
            ["Pending", "In Progress", "Completed"]
        )

        # ==========================================
        # UPDATE ALL
        # ==========================================
        if update_all:

            if st.button("Update All Rows"):

                for _, row in result_df.iterrows():
                    update_status(
                        row["Document Number"],
                        row["Sl No"],
                        new_status
                    )

                st.cache_data.clear()
                st.success("All rows updated successfully ✅")
                st.rerun()

        # ==========================================
        # UPDATE INDIVIDUAL
        # ==========================================
        else:

            selected_slno = st.selectbox(
                "Select Sl No to Update",
                result_df["Sl No"].tolist()
            )

            if st.button("Update Selected Row"):

                update_status(
                    document_number,
                    selected_slno,
                    new_status
                )

                st.cache_data.clear()
                st.success("Selected row updated successfully ✅")
                st.rerun()




