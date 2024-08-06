import os
import re

from operator import itemgetter
from dotenv import load_dotenv
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

load_dotenv()

# main logic
# product & service then
# average -> generate query

# Connect with the database
db = SQLDatabase.from_uri(os.environ["DB_URL"])
# LLM configuration
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)





# variations in data

# template for sql query generation
template = """
You are a {dialect} expert. Given an input question, create a syntactically correct {dialect} query to run.
Follow the instructions below:
    - Service and Hardware information can be present in item or hardware column, so check on both columns.
    - Return me all the column of rows. since, maybe we need all information.
    - Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per {dialect}. 
    - Order the results to return the most informative/relevant.
    - Query only those columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    - Pay attention to use only the column names you can see in the tables below.
    - Be careful to not query for columns that do not exist.

Use the following format:
    SQLQuery: SQL Query

Only use the following tables: {table_info}
Question: {input}
Note:
    1. If you are using columns relevant to cost, then include the currency column too.
    2. If the question involves a service or hardware, use the LIKE keyword in the query to provide relevant results.
    3. If information is not found in the item column, check the description column before forming the SQL query.
    4. Ensure that the query includes both item and description checks if applicable.
"""
prompt = ChatPromptTemplate.from_messages(
    [("system", template)]
).partial(dialect=db.dialect, table_info='singtel_data')

# template for answering the question
answer_template = """
    Use the following to properly answer the user's question:
        - Question: {question}    
        - Result: {result}

    Note: 
        1. if you are not able to find answer, reply "Not able to find the hardware or service information".
        2. Do not hallucinate or make the answers.
        3. Do not answer those questions which is not from our table/content.
"""
answer_prompt = PromptTemplate.from_template(answer_template)

execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db, prompt=prompt) | parse_final_answer
chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query")
        # result=itemgetter("query") | execute_query
    )
    # | answer_prompt
    # | llm
    # | StrOutputParser()
)

questions_list = [
    {"question": "Could you tell me the unit cost and supplier for the device identified as Cisco Catalyst C9999-1N-4T, specifically in Hong Kong?"},
    {"question": "What is the total expenditure and quantity available for the Cisco DNA Advantage On-Prem Lic 5Y in Hong Kong?"},
    {"question": "I'd like to know the detailed description and the currency used for the Cisco Catalyst 8500 Series in Hong Kong. Can you help?"},
    {"question": "For the 1000BASE-LX/LH SFP transceiver module in Hong Kong, could you provide the unit cost and the supplier details?"},
    {"question": "What's the total cost and the amount procured for the 1000BASE-SX SFP transceiver module in Hong Kong?"},
    {"question": "Can you give me the description and the currency information for the 10GBASE-SR SFP Module purchased in Hong Kong?"},
    {"question": "I'm looking for the unit cost and supplier for the 10GBASE-SR SFP Module, Industrial Temperature variant in Hong Kong. Could you assist?"},
    {"question": "Please provide the total expenditure and quantity for the 10GBASE-LR SFP Module, Enterprise-Class in Hong Kong."},
    {"question": "What would be the average unit cost for all devices supplied by DDD Cheng in Hong Kong?"},
    {"question": "Can you calculate the total quantity of all items quoted under QUO-1212546-G6C7S5001 in Hong Kong?"},
    {"question": "If we combine the total costs of the Cisco Catalyst C9999-1N-4T and the Cisco Catalyst 8500 Series, what would the combined cost be in Hong Kong?"},
    {"question": "What's the average total cost of items that have a quantity greater than 5 in Hong Kong?"},
    {"question": "How many different items have a unit cost (USD) below 10 in Hong Kong?"}
]
result = chain.invoke(questions_list[-3])
print("-----------------------------------------------------------------------------------------------")
print(result)
print("-----------------------------------------------------------------------------------------------")
