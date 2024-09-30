# To run this example, make sure you run this in command line:
# pip install -r requirements.txt
# Then run the streamlit with this command:
# streamlit run streamlit-example.py
# (make sure you get the path to this .py file correct)

import os
import shutil
import streamlit as st
import tempfile
from dotenv import load_dotenv
from streamlit_chat import message
from tripadvisor import get_nearby_attraction
from tripadvisor import get_nearby_hotel
from tripadvisor import get_nearby_restaurants
from tripadvisor import get_location_info
from tripadvisor import get_location_reviews
from tripadvisor import get_location_photos
from flights import get_airport_id
from flights import getFlightToken
from flights import getFlightInfo


from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, create_openai_tools_agent
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage

# Store OpenAI API key
load_dotenv()
st.session_state['openai_api_key'] = os.getenv("OPENAI_API_KEY") # Get the api key from .env file and store it in a session variable
if not st.session_state['openai_api_key']: # Check the api key exists
    st.error("OpenAI API key not found")
    st.stop()

# Title
st.title("Trip Planner")

# Initialize chat history
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hello"]

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey"]

# Create sidebar for saving locations
# st.sidebar.title("Saved Locations")
# locations = {}
# for location in locations:
#     with st.sidebar:
#         st.text(location)

# Initialize a LangChain chat agent
llm = ChatOpenAI(temperature=0)
tools = [get_nearby_restaurants, get_nearby_hotel, get_nearby_attraction, get_location_info, get_location_reviews, get_location_photos, get_airport_id, getFlightToken, getFlightInfo]
prompt = hub.pull("hwchase17/openai-tools-agent")

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Create streamlit containers for chat history and user input
response_container = st.container()
container = st.container()

# Display user input area
with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Input", placeholder="Enter a message", key='input', label_visibility="collapsed")
        submit_button = st.form_submit_button(label='Send')

    # This runs when user enters message to chat bot
    if submit_button and user_input:
        # Get a response from the llm, by giving the user message and chat history to the agent
        # user_input += ". The response must be only the titles of three locations in a numbered list and nothing else."
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": st.session_state['history']
        })

        # st.text = st.text() + result["output"]

        # Add the user message and llm response to the chat history
        st.session_state['history'].append(HumanMessage(content=user_input))
        st.session_state['history'].append(AIMessage(result["output"]))

        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(result["output"])


# Dislplay chat history
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="fun-emoji")
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts")


# At the end of the session or when you're done with the file, clean up the temporary files
def clean_up_files():
    if 'file_paths' in st.session_state:
        for file_path in st.session_state['file_paths'].values():
            if os.path.exists(file_path):
                os.remove(file_path)
