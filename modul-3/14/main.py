import os
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.tools import tool
from datetime import datetime
from langchain.agents import create_agent

load_dotenv()
try:
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["QDRANT_API_KEY"] = os.getenv("QDRANT_API_KEY")
    os.environ["QDRANT_URL"] = os.getenv("QDRANT_HOST")
except:
    os.environ["OPENAI_API_KEY"] = st.text_input("Enter your API Key:", type="password")
    os.environ["QDRANT_API_KEY"] = st.text_input("Enter your API Key:", type="password")
    os.environ["QDRANT_URL"] = st.text_input("Enter your URL:", type="password")

model = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#setup qdrant client
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="product_documents",
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
    check_compatibility=False
)

@tool
def current_datetime():
  """Tool for retrieving the current date and time information."""
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def promo_list():
  """Use this tool for get information about promo details per day."""
  promo = '''List of dicount everyday:
* Monday: Discount 50% for all product!
* Tuesday: Free shipping cost for total payment over Rs. 200.
* Wednesday: Buy 2 Get 1 Free for all product!
* Thrusday: Free shipping cost for total payment over Rs. 100.
* Friday: Discount 30% for all product!
* Saturday: Free shipping cost for total payment over Rs. 150.
* Sunday: Discount 20% for all product!
'''
  return promo

@tool
def check_relevant_products(query: str):
  """Tool for retrieving informations about relevant products in the store."""
  documents = qdrant.similarity_search(query, k=10)
  docs = [d.page_content for d in documents]
  return docs

tools = [check_relevant_products, promo_list, current_datetime]
agent = create_agent(model, tools, system_prompt="You are a clothing store assistant, please politely answer the question. Always run current_datetime tool at first step to answer User's question.")

st.title("🛍️ Clothing Store Assistant")

if os.environ["OPENAI_API_KEY"]:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_U := st.chat_input("How can I help you?"):
        with st.chat_message("Human"):
            st.markdown(prompt_U)

        st.session_state.messages.append({"role": "Human", "content": prompt_U})
        
        with st.chat_message("AI"):
            response = agent.invoke({"messages": [{"role": "user", "content": prompt_U}]})
            answer = response["messages"][-1].content
            st.markdown(answer)
        st.session_state.messages.append({"role": "AI", "content": answer})