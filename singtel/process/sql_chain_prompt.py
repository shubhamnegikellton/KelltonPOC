table_info = """
table name: singtel_data
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
# Create the SQL Query
prompt_template = """
You are a {dialect} expert. Given an input question, create a syntactically correct {dialect} query to run.
Please review the following points before creating the query:
    - Ensure to check both item and description columns if applicable, and include appropriate joins, group by clauses, or other SQL constructs where necessary.
    - Convert any plural terms in the question to their singular form before generating the query. For example, "routers" should be converted to "router".
    - Use the `unit_cost_usd` column for all calculations related to total, cost, and average etc.Also, exclude the `currency` column from query.
    - Query only those columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    - Return all columns except "id," since we may need all information.
    - Unless the user specifies a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per {dialect}.
    - For complex queries involving aggregation, calculations, or summaries, include the necessary aggregate functions such as SUM, COUNT, AVG, etc., and ensure the query is syntactically correct.
    - Prioritize the results to return those that are most closely aligned with our query.
    - Pay attention to use only the column names you can see in the tables below.
    - If the query is not returning the expected results, ensure that the SQL syntax is correct, the column names and data types match the schema, and that the logic aligns with the query requirements.
    - You don't have update, delete, or create permissions.

Use the following format:
    SQLQuery: SQL Query

Only use the following tables: {table_info}
Question: {input}
Note:
    1. Search in the item and description columns unless a specific column is provided.
    2. If the query involves cost-related columns, include the currency column in the results as well.
    3. Use the ILIKE keyword in the query if the question pertains to service or hardware details to match relevant records.
    4. If the required information is not found in the item column, check the description column for additional details.
    5. Make sure to include both item and description checks in the query if the question is relevant to both columns.
    6. For queries involving aggregation, apply the necessary aggregate functions (e.g., SUM, COUNT, AVG) and use GROUP BY clauses where appropriate.
    7. Ensure the query uses only the columns present in the table schema to avoid errors and ensure accurate results.
"""

# template for answering the question
answer_template = """
    Use the following to properly answer the user's question:
        - Question: {question}
        - Result: {result}
    
    Ouptut: if table format needed then use it otherwise show in statement.
    
    Note:
    1. Answer the following question only if it pertains to the provided table or results; otherwise, respond with 'I cannot answer this question as it is not related to us. 
    2. Do not hallucinate or make the answers.
"""
