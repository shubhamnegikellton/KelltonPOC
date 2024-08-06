import os
import streamlit as st
import pandas as pd
import numpy as np

from navigation import make_sidebar
from singtel.process.main import process_format_a, process_format_b, process_format_c
from singtel.db.db_connection import connect_to_db, insert_data
from utilities import use_header

# Progress bar for steps
pd.set_option('future.no_silent_downcasting', True)
steps = ["First", "Second", "Third"]
step_descriptions = ["Upload", "View & Update", "Success"]
column_mapping = {
    'Item': 'item',
    'Description': 'description',
    'Total Cost': 'total_cost',
    'QTY': 'quantity',
    'Date': 'date',
    'Country': 'country',
    'City': 'city',
    'Supplier': 'supplier',
    'Quote #': 'quote_id',
    'Currency': 'currency',
    'Hours': 'hours',
    'Unit Cost': 'unit_cost',
    'Unit Cost (USD)': 'unit_cost_usd'
}
connection = connect_to_db()


def replace_empty_with_none(df):
    """Replace empty strings with None (NULL) in a DataFrame."""
    df.replace("", np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)
    return df


def show_progress_bar(current_step, steps, step_descriptions):
    num_steps = len(steps)
    columns = st.columns(num_steps * 2 - 1)

    for i in range(num_steps):
        with columns[i * 2]:
            st.markdown(f"""
            <div class="step">
                <div class="step-number {'done' if i <= current_step else ''}">{i + 1}</div>
                <div class="step-description {'done' if i <= current_step else ''}">{step_descriptions[i]}</div>
            </div>
            """, unsafe_allow_html=True)

        if i < num_steps - 1:
            with columns[i * 2 + 1]:
                st.markdown(f"""
                <div class="step-line-container">
                    <div class="step-line {'done' if i < current_step else ''}"></div>
                </div>
                """, unsafe_allow_html=True)

    # CSS Styling
    st.markdown("""
    <style>
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .step-number {
        background-color: #4bb0ff;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .step-number.done {
        background-color: #4CAF50;
    }
    .step-description {
        font-size: 14px;
        margin-top: 5px;
    }
    .step-description.done {
        color: #4CAF50;
    }
    .step-line-container {
        display: flex;
        align-items: center;
        height: 30px; /* Adjust height as needed to vertically center align the line */
    }
    .step-line {
        height: 2px;
        background-color: #6c63ff;
        flex-grow: 1;
        margin: 0 10px;
    }
    .step-line.done {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# show header
use_header()

# show sidebar
make_sidebar()

# Show progress bar
show_progress_bar(st.session_state.current_step - 1, steps, step_descriptions)

if st.session_state.current_step == 1:
    with st.form("upload_form"):
        st.markdown("#### Select Template")
        template = st.selectbox("Select Template", ["Template A", "Template B", "Template C"], key="template")
        uploaded_file = st.file_uploader("Choose file", type=["xls", "xlsx"], key="file")
        submitted = st.form_submit_button("Upload")

        if submitted:
            if uploaded_file is None:
                st.error("Please upload a file before proceeding.")
            else:
                with st.spinner(text="In progress..."):
                    if template == "Template A":
                        response = process_format_a(uploaded_file)
                    elif template == "Template B":
                        response = process_format_b(uploaded_file)
                    elif template == "Template C":
                        response = process_format_c(uploaded_file)

                st.session_state.uploaded_file = response
                st.success("File uploaded successfully!")
                st.session_state.current_step = 2
                st.query_params['step'] = st.session_state.current_step
                st.rerun()

elif st.session_state.current_step == 2:
    # Display uploaded data
    if st.session_state.uploaded_file is not None:
        df = st.session_state.uploaded_file
        df = st.data_editor(df, num_rows="dynamic")

        col1, col2 = st.columns([9,1])
        with col1:
            if st.button("Back"):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            response = None
            if st.button("Next"):
                with st.spinner(text="In progress..."):
                    df_rearranged = df.rename(columns=column_mapping)
                    df_rearranged = df_rearranged[list(column_mapping.values())]
                    df_rearranged['quantity'] = pd.to_numeric(df_rearranged['quantity'].replace('', np.nan),
                                                                errors='coerce')
                    df_rearranged['hours'] = pd.to_numeric(df_rearranged['hours'].replace('', np.nan),
                                                            errors='coerce')
                    df_rearranged = replace_empty_with_none(df_rearranged)
                    st.session_state.records = len(df_rearranged)
                    for col in df_rearranged.columns:
                        df_rearranged[col] = df_rearranged[col].map(lambda x: None if pd.isna(x) else x)
                    data_tuples = df_rearranged.to_records(index=False).tolist()
                    response = insert_data(connection, data_tuples)
                    if response.startswith("Error"):
                        st.error(response)
                    else:
                        st.session_state.current_step = 3
                        st.rerun()

elif st.session_state.current_step == 3:
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, '../singtel/static/success-icon.png')
    file_path = os.path.abspath(file_path)
    # Display success message
    with st.spinner(text="In progress..."):
        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 3, 5], vertical_alignment="center")
            with col2:
                st.image(file_path, width=100)
            st.markdown(f"""
            <div style="text-align: center;padding: 5px 5px; margin-bottom: 10px;">
                <h3>File is successfully uploaded</h3>
                <p>{st.session_state.records} records processed</p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([5, 3, 5], vertical_alignment="center")
            with col2:
                if st.button("Upload New File"):
                    st.session_state.current_step = 1
                    st.rerun()
        st.stop()
