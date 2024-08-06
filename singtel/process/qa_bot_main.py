import os
from operator import itemgetter

from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from .sql_chain_prompt import answer_template, prompt_template, table_info
from .utility import parse_final_answer, log_output


def qa_chatbot_response(message, stream_callback=None):
    # Connect with the database
    db = SQLDatabase.from_uri(os.environ["DB_URL"])

    # LLM configuration with streaming enabled
    llm = ChatOpenAI(model="gpt-4o", temperature=0, stream=True)

    # query prompt update with values
    prompt = ChatPromptTemplate.from_messages([("system", prompt_template)]).partial(
        dialect=db.dialect, table_info=table_info
    )

    answer_prompt = PromptTemplate.from_template(answer_template)

    execute_query = QuerySQLDataBaseTool(db=db) | log_output
    write_query = create_sql_query_chain(llm, db, prompt=prompt) | parse_final_answer
    chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer_prompt
            | llm
            | StrOutputParser()
    )

    query = message[-1]["content"]

    # Custom function to handle streaming
    if stream_callback:
        partial_result = ""
        for chunk in chain.stream({"question": query}):
            partial_result += chunk
            stream_callback(partial_result)
        return partial_result
    else:
        result = chain.invoke({"question": query})
        return result
