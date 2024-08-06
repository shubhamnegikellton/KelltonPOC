import streamlit as st


def use_header():
    header = st.container()
    with header:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write("")
            st.image("https://awsmp-logos.s3.amazonaws.com/0ba0cfff-f9da-474c-9aea-7ce69f505034/9c50547121ad1016ef9c6e9ef9804cdc.png")
        st.caption("🚀 An App powered by Kellton")
        st.write("<div class='fixed-header'/>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
            div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                position: sticky;
                top: 2.875rem;
                background-color: white;
                z-index: 999;
            }
        </style>
        """,
        unsafe_allow_html=True
    )