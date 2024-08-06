import streamlit as st
from time import sleep
from navigation import make_sidebar

make_sidebar()

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.image("https://awsmp-logos.s3.amazonaws.com/0ba0cfff-f9da-474c-9aea-7ce69f505034/9c50547121ad1016ef9c6e9ef9804cdc.png")

st.write("Please log in to continue.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Log in", type="primary"):
    uid = st.secrets["user_id"]
    pwd = st.secrets["password"]

    if username == uid and password == pwd:
        st.session_state.logged_in = True
        if "current_step" not in st.session_state:
            st.session_state.current_step = 1
            st.session_state.records = 0
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = None
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/upload_screen.py")
    else:
        st.error("Incorrect username or password")
