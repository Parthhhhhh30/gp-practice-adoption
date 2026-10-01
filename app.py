import streamlit as st

st.set_page_config(
    page_title="Practice Growth Workspace",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from workspace import run

run()
