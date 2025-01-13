import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from fetch_xml import download_xml
from loguru import logger

doc_count = 0
xml_keys = [
    "103/4358e331f543193440f7c1079da8340a/main.xml",
    "101/a59d184cf9cc2cfecb331c7cd5a864fe/main.xml",
    "1948/2ef55d9483753350b06babffe4398b1d/main.xml",
    "2411/5aa58b4e43cde8bb9d30d5ae5d9df161/main.xml",
    "316/bf55ae07c86b2ca8f77ffb1c73c5aeb7/main.xml",
    "2411/650574620140779d010f0f0dd5d1e953/main.xml",
    "95/7afc742ac66003fb5cf5ee0da30c49ce/main.xml"
]
for xml_key in xml_keys:
    if download_xml(xml_key):
        doc_count+=1

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")
st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Ask me a question about these {doc_count} infrastructure contracts!",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
    logger.info(reader.input_files)
    docs = reader.load_data(show_progress=True)
    Settings.llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        system_prompt=f"""You are a laywer and 
        have been given {doc_count} infrastructure agreements in XML format.
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
