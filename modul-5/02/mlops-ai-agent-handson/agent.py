"""
Simple LangChain Agent Module
This module contains the core agent logic using LangChain
"""

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
import os

class SimpleAgent:
    def __init__(self, openai_api_key=None):
        """
        Initialize the Simple Agent
        
        Args:
            openai_api_key (str): OpenAI API key. If None, will use environment variable OPENAI_API_KEY
        """
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize the LLM
        # The legacy completion model (gpt-3.5-turbo-instruct) was shut down by OpenAI
        # on 2026-09-28, so we use a chat model. The model name can be changed without
        # editing code: docker run -e OPENAI_MODEL=<model-name> ...
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=0.7)
        
        # Define tools for the agent
        self.tools = [
            Tool(
                name="Calculator",
                description="Useful for mathematical calculations. Input should be a mathematical expression.",
                func=self.calculate
            ),
            Tool(
                name="Text Analyzer",
                description="Useful for analyzing text. Input should be a text string to analyze.",
                func=self.analyze_text
            )
        ]
        
        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    def calculate(self, expression):
        """
        Simple calculator function
        
        Args:
            expression (str): Mathematical expression to evaluate
            
        Returns:
            str: Result of the calculation
        """
        try:
            # Simple evaluation for basic math operations
            # In production, use a proper math parser for security
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    def analyze_text(self, text):
        """
        Simple text analysis function
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Analysis result
        """
        word_count = len(text.split())
        char_count = len(text)
        return f"Text Analysis:\n- Word count: {word_count}\n- Character count: {char_count}\n- Text: {text[:100]}{'...' if len(text) > 100 else ''}"
    
    def chat(self, message):
        """
        Process a chat message through the agent
        
        Args:
            message (str): User message
            
        Returns:
            str: Agent response
        """
        try:
            response = self.agent.run(input=message)
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def get_chat_history(self):
        """
        Get the conversation history
        
        Returns:
            str: Formatted chat history
        """
        if hasattr(self.memory, 'chat_memory') and self.memory.chat_memory.messages:
            history = []
            for message in self.memory.chat_memory.messages:
                role = "Human" if message.type == "human" else "AI"
                history.append(f"{role}: {message.content}")
            return "\n".join(history)
        return "No conversation history available."
