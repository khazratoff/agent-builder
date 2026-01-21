"""
FastAPI server for the multi-agent system with SSE streaming.

This module provides a REST API endpoint that streams agent responses
using Server-Sent Events (SSE).
"""

import os
import sys
import logging
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Add src to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Suppress INFO logs from MCP and related libraries
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp-weather").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

from core.supervisor import SupervisorWorkflow
from core.agent_registry import AgentRegistry

# Import agents to trigger registration
import agents

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent System API",
    description="API for interacting with the multi-agent system",
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

# Global supervisor instance
supervisor: SupervisorWorkflow = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    agent_used: str
    thread_id: str


@app.on_event("startup")
async def startup_event():
    """Initialize the supervisor on startup."""
    global supervisor

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found in environment variables")

    print("\n🔧 Initializing multi-agent system...")

    try:
        supervisor = SupervisorWorkflow(model="gpt-4o")
        app_instance = supervisor.build()
        print("✅ Multi-agent system ready!")

        # List registered agents
        agents_list = AgentRegistry.get_all_agents()
        print(f"📋 Registered agents: {', '.join([a.name for a in agents_list])}\n")

    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Multi-Agent System API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send a message and get response",
            "/stream": "POST - Send a message and get streamed response (SSE)",
            "/agents": "GET - List all registered agents",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "supervisor_initialized": supervisor is not None
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    agents_list = AgentRegistry.get_all_agents()

    return {
        "count": len(agents_list),
        "agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities
            }
            for agent in agents_list
        ]
    }


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint.

    Send a message and receive the complete response.
    """
    if not supervisor:
        raise HTTPException(status_code=500, detail="Supervisor not initialized")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Execute the request through the supervisor
        result = await asyncio.to_thread(
            supervisor.invoke,
            request.message,
            thread_id=request.thread_id
        )

        return ChatResponse(
            response=result.get("agent_output", "No response generated"),
            agent_used=result.get("current_agent", "unknown"),
            thread_id=request.thread_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


async def generate_stream_text(message: str, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Generate streaming plain text response.

    Args:
        message: User message
        thread_id: Thread ID for conversation context

    Yields:
        Plain text chunks with agent metadata
    """
    try:
        # Execute the request through the supervisor
        result = await asyncio.to_thread(
            supervisor.invoke,
            message,
            thread_id=thread_id
        )

        # First, send agent name as metadata (special format)
        agent_name = result.get("current_agent", "unknown")
        yield f"__AGENT__:{agent_name}\n"

        await asyncio.sleep(0.1)

        # Stream the response word by word for natural reading experience
        response_text = result.get("agent_output", "No response generated")

        # Split by words for more natural streaming
        words = response_text.split()
        buffer = ""

        for i, word in enumerate(words):
            buffer += word + " "

            # Send chunks of 3-5 words
            # if (i + 1) % 4 == 0 or i == len(words) - 1:
            yield buffer
            buffer = ""
            await asyncio.sleep(0.1)  # Natural reading delay

    except Exception as e:
        # Send error as plain text
        yield f"Error: {str(e)}"


@app.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    Streaming chat endpoint with plain text response.

    Send a message and receive a streamed response.
    """
    if not supervisor:
        raise HTTPException(status_code=500, detail="Supervisor not initialized")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return StreamingResponse(
        generate_stream_text(request.message, request.thread_id),
        media_type="text/plain"
    )


if __name__ == "__main__":
    import uvicorn

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🚀 Multi-Agent System API Server 🚀                 ║
║                                                              ║
║          FastAPI with SSE Streaming Support                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
