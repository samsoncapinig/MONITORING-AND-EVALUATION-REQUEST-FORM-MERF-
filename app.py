
# MERF Request Form (Public)
import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

st.set_page_config(page_title="MONITORING AND EVALUATION REQUEST FORM (MERF)")
st.title("MONITORING AND EVALUATION REQUEST FORM (MERF)")

DATA_FILE = "data/records.csv"
MEMO_DIR = "uploads/memorandum"
ACTIVITY_DIR = "uploads/activity_matrix"

os.makedirs("data", exist_ok=True)
os.makedirs(MEMO_DIR, exist_ok=True)
os.makedirs(ACTIVITY_DIR, exist_ok=True)

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Reference No","Program Owner","Training Title","Venue",
        "Date Start","Date End","Memorandum File","Activity Matrix File",
        "Status","Admin Remarks","Timestamp"
    ])

def generate_ref(df):
    year = datetime.now().year
    return f"MERF-{year}-{len(df)+1:04d}"

SENDER_EMAIL = st.secrets["EMAIL_ADDRESS"]
SENDER_PASSWORD = st.secrets["EMAIL_PASSWORD"]
RECIPIENTS = ["samson.capinig001@deped.gov.ph"]

def send_email(record):
    msg = EmailMessage()
    msg["Subject"] = f"📢 NEW MERF REQUEST – {record['Reference No']}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)
    msg.set_content(f"""
    New MERF request submitted.

    Reference No: {record['Reference No']}
    Program Owner: {record['Program Owner']}
    Training Title: {record['Training Title']}
    Venue: {record['Venue']}
    Dates: {record['Date Start']} to {record['Date End']}
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

with st.form("merf_form"):
    program_owner = st.text_input("Program Owner")
    training_title = st.text_input("Training Title")
    venue = st.text_input("Venue")
    date_start = st.date_input("Date Start")
    date_end = st.date_input("Date End")
    memo = st.file_uploader("Upload Memorandum (PDF)", type=["pdf"])
    activity = st.file_uploader("Upload Activity Matrix (PDF)", type=["pdf"])
    submit = st.form_submit_button("Submit Request")

if submit:
    if memo and activity:
        ref = generate_ref(df)
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        memo_name = f"{ts}_{memo.name}"
        act_name = f"{ts}_{activity.name}"

        open(os.path.join(MEMO_DIR, memo_name), "wb").write(memo.getbuffer())
        open(os.path.join(ACTIVITY_DIR, act_name), "wb").write(activity.getbuffer())

        record = {
            "Reference No": ref,
            "Program Owner": program_owner,
            "Training Title": training_title,
            "Venue": venue,
            "Date Start": date_start,
            "Date End": date_end,
            "Memorandum File": memo_name,
            "Activity Matrix File": act_name,
            "Status": "Pending",
            "Admin Remarks": "",
            "Timestamp": datetime.now().isoformat()
        }

        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        send_email(record)
        st.success(f"Request submitted successfully. Reference No: {ref}")
    else:
        st.error("Both PDF files are required.")
