import streamlit as st
import requests
import sys

st.set_page_config(page_title="DataExpiry Diagnostic")

st.title("DataExpiry Diagnostic")
st.success("Streamlit started successfully.")

st.write("Streamlit version:", st.__version__)
st.write("Python version:", sys.version)

st.write("Requests version:", requests.__version__)
