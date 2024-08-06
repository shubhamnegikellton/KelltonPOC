import streamlit as st

from singtel.process.qa_bot_main import qa_chatbot_response
from navigation import make_sidebar
from utilities import use_header

# show header
use_header()

# show sidebar
make_sidebar()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response_placeholder = st.chat_message("assistant").empty()

    def streaming_callback(partial_result):
        response_placeholder.write(partial_result)

    # Call the chatbot response function with streaming
    msg = qa_chatbot_response(message=st.session_state.messages, stream_callback=streaming_callback)

    st.session_state.messages.append({"role": "assistant", "content": msg})
    response_placeholder.write(msg)
