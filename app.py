import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- App Config ---
st.set_page_config(
    page_title="MONITORING AND EVALUATION REQUEST FORM (MERF)",
    layout="centered"
)

st.title("📋 MONITORING AND EVALUATION REQUEST FORM (MERF)")

# --- Email Settings ---
SENDER_EMAIL = st.secrets["EMAIL_ADDRESS"]
SENDER_PASSWORD = st.secrets["EMAIL_PASSWORD"]

RECIPIENTS = [
    "samson.capinig001@deped.gov.ph",
    # Add more emails here:
    # "another.email@deped.gov.ph"
]

# --- Paths ---
DATA_FILE = "data/records.csv"
MEMO_DIR = "uploads/memorandum"
ACTIVITY_DIR = "uploads/activity_matrix"

os.makedirs("data", exist_ok=True)
os.makedirs(MEMO_DIR, exist_ok=True)
os.makedirs(ACTIVITY_DIR, exist_ok=True)

# --- Load Data ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Program Owner",
        "Training Title",
        "Venue",
        "Date Start",
        "Date End",
        "Memorandum File",
        "Activity Matrix File",
        "Timestamp"
    ])

# --- Email Function ---
def send_email(record):
    msg = EmailMessage()
    msg["Subject"] = "📢 New MERF Submission Received"
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    msg.set_content(f"""
A new Monitoring and Evaluation Request has been submitted.

Program Owner: {record['Program Owner']}
Training Title: {record['Training Title']}
Venue: {record['Venue']}
Date Start: {record['Date Start']}
Date End: {record['Date End']}
Submitted On: {record['Timestamp']}

Please log in to the MERF system to review the request.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

# --- Form ---
with st.form("merf_form"):
    program_owner = st.text_input("Program Owner")
    training_title = st.text_input("Training Title")
    venue = st.text_input("Venue")
    date_start = st.date_input("Date Start")
    date_end = st.date_input("Date End")

    memorandum = st.file_uploader("Upload Memorandum (PDF)", type=["pdf"])
    activity_matrix = st.file_uploader("Upload Activity Matrix (PDF)", type=["pdf"])

    submitted = st.form_submit_button("Submit Request")

if submitted:
    if not memorandum or not activity_matrix:
        st.error("❌ Both PDF files are required.")
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        memo_filename = f"{timestamp}_{memorandum.name}"
        activity_filename = f"{timestamp}_{activity_matrix.name}"

        with open(os.path.join(MEMO_DIR, memo_filename), "wb") as f:
            f.write(memorandum.getbuffer())

        with open(os.path.join(ACTIVITY_DIR, activity_filename), "wb") as f:
            f.write(activity_matrix.getbuffer())

        new_record = {
            "Program Owner": program_owner,
            "Training Title": training_title,
            "Venue": venue,
            "Date Start": date_start,
            "Date End": date_end,
            "Memorandum File": memo_filename,
            "Activity Matrix File": activity_filename,
            "Timestamp": datetime.now().isoformat()
        }

        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        send_email(new_record)

        st.success("✅ Request submitted successfully. Email notification sent.")

# --- Records Table ---
st.subheader("📊 Submitted Requests")
st.dataframe(df)

# --- Excel Download ---
st.subheader("⬇️ Download Records")
excel_file = df.to_excel(index=False, engine="openpyxl")

st.download_button(
    "Download Excel",
    excel_file,
    "MERF_Records.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
