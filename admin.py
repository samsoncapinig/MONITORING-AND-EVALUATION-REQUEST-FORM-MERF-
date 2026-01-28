
# MERF Admin Dashboard
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MERF Admin Dashboard")

if "auth" not in st.session_state:
    st.session_state.auth = False

password = st.text_input("Admin Password", type="password")

if password == st.secrets["ADMIN_PASSWORD"]:
    st.session_state.auth = True

if not st.session_state.auth:
    st.stop()

df = pd.read_csv("data/records.csv")

st.title("MERF Admin Dashboard")

pending = df[df["Status"] == "Pending"]
st.dataframe(pending)

ref = st.selectbox("Select Reference No", pending["Reference No"])
remarks = st.text_area("Admin Remarks")

if st.button("Approve"):
    df.loc[df["Reference No"] == ref, ["Status","Admin Remarks"]] = ["Approved", remarks]
    df.to_csv("data/records.csv", index=False)
    st.success("Request Approved")

if st.button("Return"):
    df.loc[df["Reference No"] == ref, ["Status","Admin Remarks"]] = ["Returned", remarks]
    df.to_csv("data/records.csv", index=False)
    st.warning("Request Returned")
