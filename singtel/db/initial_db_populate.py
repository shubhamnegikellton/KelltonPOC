import os

import psycopg2
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection parameters from environment variables
cred_prefix=""
if st.secrets['is_local']:
    cred_prefix = "local_db"
else:
    cred_prefix = "server_db"

dbname = st.secrets[cred_prefix]['DB_NAME']
user = st.secrets[cred_prefix]['DB_USER']
password = st.secrets[cred_prefix]['DB_PASSWORD']
host = st.secrets[cred_prefix]['DB_HOST']
port = st.secrets[cred_prefix]['DB_PORT']

# SQL command to create the table
create_table_query = """
CREATE TABLE singtel_data (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    item VARCHAR(255) NOT NULL,
    description TEXT,
    country VARCHAR(255),
    city VARCHAR(255),
    supplier VARCHAR(255),
    quote_id VARCHAR(255),
    currency VARCHAR(3),
    total_cost NUMERIC(20, 2),
    quantity INTEGER,
    hours INTEGER,
    unit_cost NUMERIC(20, 2),
    unit_cost_usd NUMERIC(20, 2)
);
"""

connection = None
cursor = None
try:
    connection = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )

    # Create a new database session and return a new instance of the connection class
    cursor = connection.cursor()
    # Execute the SQL command to create the table
    cursor.execute(create_table_query)
    # Commit the transaction
    connection.commit()

    print("Table created successfully in PostgreSQL")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"Error while creating PostgreSQL table: {error}")
finally:
    # Close the database connection
    if connection is not None:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
