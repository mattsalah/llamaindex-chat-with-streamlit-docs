import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from fetch_data import download_data
from loguru import logger

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")
st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me a question about the selected infrastructure contracts!",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    input_files = download_data()
    reader = SimpleDirectoryReader(input_files=input_files, recursive=True)
    docs = reader.load_data(show_progress=True)
    logger.info(reader.input_files)
    doc_count = len(reader.input_files)
    if doc_count==1:
        Settings.llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            system_prompt="""You are a laywer and 
            have been given an infrastructure agreements.
            Your job is to answer technical questions about this agreement.
            Assume that all questions are related 
            to the agreement. Keep 
            your answers technical and based on 
            the text of the document – do not hallucinate features. 
            """
        )
    else:
        Settings.llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            system_prompt=f"""You are a laywer and 
            have been given {doc_count} infrastructure agreements.
            Your job is to answer technical questions about the agreements.
            Assume that all questions are related 
            to these {doc_count} agreements. Keep 
            your answers technical and based on 
            the text of the documents – do not hallucinate features. 
            """
        )
    index = VectorStoreIndex.from_documents(docs)
    return index


index = load_data()

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, streaming=True
    )

if prompt := st.chat_input(
    "Ask a question"
):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Write message history to UI
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = st.session_state.chat_engine.stream_chat(prompt)
        st.write_stream(response_stream.response_gen)
        message = {"role": "assistant", "content": response_stream.response}
        # Add response to message history
        st.session_state.messages.append(message)
