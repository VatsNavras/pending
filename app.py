import streamlit as st
from sheets import load_sheet

st.set_page_config(
    page_title="Pending Order ERP",
    layout="centered"
)

# ---------- CSS ----------
st.markdown("""
<style>
body { background-color:#f4f6f8; }
.card {
    background:white;
    padding:16px;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
    margin-bottom:16px;
}
.label { font-size:12px; color:#6c757d; font-weight:600; }
.value { font-size:14px; font-weight:600; word-wrap:break-word; }
.metric { font-size:20px; font-weight:700; color:#0d6efd; }
.header { font-size:18px; font-weight:700; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
df = load_sheet()

st.markdown("<div class='header'>📦 Pending Order Dashboard</div>", unsafe_allow_html=True)

# ---------- Master Dropdown ----------
doc_numbers = sorted(df["Document Number"].astype(str).unique())
doc = st.selectbox("Document Number", doc_numbers)

doc_df = df[df["Document Number"].astype(str) == doc]

# ---------- SLNo Dropdown ----------
sl_no = st.selectbox(
    "SL No",
    doc_df["SLNo"].astype(str).unique()
)

row = doc_df[doc_df["SLNo"].astype(str) == sl_no].iloc[0]

# ---------- ERP Card ----------
st.markdown(f"""
<div class="card">
    <div class="label">Party Name</div>
    <div class="value">{row['Party Name']}</div>

    <hr>

    <div class="label">Part Name</div>
    <div class="value">{row['Part Name']}</div>

    <hr>

    <div class="label">Material Grade</div>
    <div class="value">{row['Material Grade']}</div>

    <div class="label">HT Priority</div>
    <div class="value">{row['HT Priority']}</div>

    <div class="label">HT Detail</div>
    <div class="value">{row['HT Detail']}</div>

    <hr>

    <div style="display:flex; justify-content:space-between; text-align:center;">
        <div>
            <div class="label">Order Qty</div>
            <div class="metric">{row['Order Qty']}</div>
        </div>
        <div>
            <div class="label">Pending Qty</div>
            <div class="metric">{row['Pending Qty']}</div>
        </div>
        <div>
            <div class="label">Delivery Date</div>
            <div class="metric">{row['DELIVERYDATE'] or '-'}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
