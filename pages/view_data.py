import streamlit as st

from navigation import make_sidebar
from singtel.db.db_connection import connect_to_db, execute_query, drop_all_data
from utilities import use_header

# show header
use_header()

# show sidebar
make_sidebar()

# connect to db
connection = connect_to_db()
select_query = "SELECT * FROM singtel_data;"
df = execute_query(connection, select_query)

if df is not None and not df.empty:
    st.write("### SingTel Data")
    if st.button("Delete Data", type="primary"):
        error_placeholder = st.empty()
        with st.spinner(text="Deletion in progress..."):
            response = drop_all_data(connection, "singtel_data")
            if response.startswith("Error"):
                error_placeholder.empty()
                error_placeholder.error(response)
            else:
                st.rerun()

    rows_per_page = 10
    total_rows = len(df)
    total_pages = (total_rows - 1) // rows_per_page + 1

    # Initialize session state for pagination if not already done
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # Calculate the start and end indices of the rows to display
    start_idx = (st.session_state.page_number - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    # Display the rows for the current page
    st.dataframe(df.iloc[start_idx:end_idx])

    col1, col2, col3 = st.columns([2, 7, 1])
    with col1:
        if st.button("Previous") and st.session_state.page_number > 1:
            st.session_state.page_number -= 1
            st.rerun()
    with col3:
        if st.button("Next  ") and st.session_state.page_number < total_pages:
            st.session_state.page_number += 1
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align: center;font-weight:bold;'>Page {st.session_state.page_number}<span style='font-weight:normal;'> of </span>{total_pages}</div>",
            unsafe_allow_html=True,
        )
else:
    st.warning("No Data Found, Please upload a file first on the Upload page.")
