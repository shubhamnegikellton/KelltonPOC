import os
import streamlit as st

import pandas as pd
import psycopg2
from psycopg2 import OperationalError


def connect_to_db():
    if st.secrets['is_local']:
        cred_prefix = "local_db"
    else:
        cred_prefix = "server_db"

    dbname = st.secrets[cred_prefix]['DB_NAME']
    user = st.secrets[cred_prefix]['DB_USER']
    password = st.secrets[cred_prefix]['DB_PASSWORD']
    host = st.secrets[cred_prefix]['DB_HOST']
    port = st.secrets[cred_prefix]['DB_PORT']

    try:
        connection = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )

        return connection
    except OperationalError as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None


def insert_data(connection, data):
    insert_query = """
    INSERT INTO singtel_data (item, description, total_cost, quantity, date, country, city, supplier, quote_id, currency, hours, unit_cost, unit_cost_usd)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.executemany(insert_query, data)
        connection.commit()
        print("Data inserted successfully into PostgreSQL")
        return "Success: Data inserted successfully into PostgreSQL"
    except (Exception, psycopg2.DatabaseError) as error:
        return f"Error: {error}"
    finally:
        if cursor is not None:
            cursor.close()


def execute_query(connection, query, data=None):
    """Execute a query and return data if it's a SELECT query."""
    cursor = None
    result = None
    try:
        cursor = connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        # Check if the query is a SELECT statement
        if query.strip().upper().startswith("SELECT"):
            # Fetch all results
            result = cursor.fetchall()
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            # Create DataFrame
            result = pd.DataFrame(result, columns=column_names)

        # Commit for queries that modify the database
        if not query.strip().upper().startswith("SELECT"):
            connection.commit()
            print("Query executed successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while executing query: {error}")
    finally:
        if cursor is not None:
            cursor.close()

    return result
