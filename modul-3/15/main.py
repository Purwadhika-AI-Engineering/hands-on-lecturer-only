# ---------------------------------------------- Importing Libraries ----------------------------------------------
import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from datetime import datetime
from langchain.agents import create_agent

# ---------------------------------------------- Setting up API Key ----------------------------------------------
load_dotenv()
try:
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
except:
    os.environ["OPENAI_API_KEY"] = st.text_input("Enter your API Key:", type="password")

# ---------------------------------------------- Creating and Tools ----------------------------------------------
model = init_chat_model("gpt-4o-mini")

#create booking hotel tool
@tool
def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

#create flight hotel tool
@tool
def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

# ---------------------------------------------- Creating Sub-Agents ----------------------------------------------
#create hotel agent
flight_assistant = create_agent(
    model=model,
    tools=[book_flight],
    system_prompt="You are a flight booking assistant",
    name="flight_assistant"
)

#create hotel agent
hotel_assistant = create_agent(
    model=model,
    tools=[book_hotel],
    system_prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

# ---------------------------------------------- Creating Supervisor Agent ----------------------------------------------
@tool
def flight_agent(from_airport: str, to_airport: str):
    """Book a flight"""
    return flight_assistant.invoke({"messages": [{"role": "user", "content": f"Book a flight from {from_airport} to {to_airport}."}]})

@tool
def hotel_agent(hotel_name: str):
    """Book a hotel"""
    return hotel_assistant.invoke({"messages": [{"role": "user", "content": f"Book a stay at {hotel_name}."}]})


supervisor = create_agent(
    tools=[flight_agent, hotel_agent], #list of agents that will helps supervisor agent
    model=model, #model for supervisor agent
    system_prompt= "You manage a hotel booking assistant and a flight booking assistant. Assign work to them." #prompt for supervisor agent
)

# ---------------------------------------------- Streamlit Interface ----------------------------------------------
st.title("🛎️ Travel Booking Assistant")

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
            final_prompt = f"""User question: {prompt_U}

Chat history:
{st.session_state.messages}"""
            response = supervisor.invoke({"messages": [{"role": "user", "content": final_prompt}]})
            answer = response["messages"][-1].content
            st.markdown(answer)
        st.session_state.messages.append({"role": "AI", "content": answer})