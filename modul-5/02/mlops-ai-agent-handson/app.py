"""
FastAPI Application for LLM Agent Service
This module contains the FastAPI web service that exposes the agent functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import SimpleAgent
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="LLM Agent Service",
    description="A simple LLM Agent service using LangChain and FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key as an environment variable")
        
        agent = SimpleAgent(openai_api_key=api_key)
        print("Agent initialized successfully!")
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        agent = None

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "LLM Agent Service is running!",
        "status": "healthy",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "history": "/history"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None
    }

@app.post("/chat")
async def chat_with_agent(message: str):
    """
    Chat endpoint for interacting with the agent
    
    Args:
        message (str): User message to send to the agent
        
    Returns:
        dict: Response from the agent
    """
    if not agent:
        raise HTTPException(
            status_code=500, 
            detail="Agent not initialized. Please check your OpenAI API key."
        )
    
    try:
        response = agent.chat(message)
        return {
            "user_message": message,
            "agent_response": response,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@app.get("/history")
async def get_chat_history():
    """
    Get the conversation history
    
    Returns:
        dict: Chat history
    """
    if not agent:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized"
        )
    
    try:
        history = agent.get_chat_history()
        return {
            "chat_history": history,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )

@app.post("/reset")
async def reset_conversation():
    """
    Reset the conversation history
    
    Returns:
        dict: Confirmation message
    """
    if not agent:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized"
        )
    
    try:
        # Reset the memory
        agent.memory.clear()
        return {
            "message": "Conversation history reset successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting conversation: {str(e)}"
        )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
