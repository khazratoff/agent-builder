# Multi-Agent System API

FastAPI server with Server-Sent Events (SSE) streaming support for the multi-agent system.

## Features

- **RESTful API** for interacting with the multi-agent system
- **SSE Streaming** for real-time response delivery
- **CORS Support** for cross-origin requests
- **Thread-based Conversations** with memory persistence
- **Multiple Agents** including file operations, research, and weather

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Running the Server

Start the server:
```bash
cd src
python api_server.py
```

The server will start on `http://127.0.0.1:8000`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the server is running and initialized.

**Response:**
```json
{
  "status": "healthy",
  "supervisor_initialized": true
}
```

### 2. List Agents
**GET** `/agents`

Get a list of all registered agents with their capabilities.

**Response:**
```json
{
  "count": 3,
  "agents": [
    {
      "name": "file_operations",
      "description": "Handles file system operations",
      "capabilities": ["read files", "write files", "list directories", ...]
    }
  ]
}
```

### 3. Chat (Non-Streaming)
**POST** `/chat`

Send a message and receive the complete response at once.

**Request Body:**
```json
{
  "message": "List all files in the current directory",
  "thread_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "Here are the files...",
  "agent_used": "file_operations",
  "thread_id": "optional_session_id"
}
```

### 4. Stream Chat (SSE)
**POST** `/stream`

Send a message and receive a streamed response using Server-Sent Events.

**Request Body:**
```json
{
  "message": "What's the weather in London?",
  "thread_id": "optional_session_id"
}
```

**SSE Events:**

- **start**: Processing started
  ```json
  {"status": "processing", "message": "Processing your request..."}
  ```

- **agent**: Agent selected
  ```json
  {"agent": "weather", "status": "Agent selected"}
  ```

- **message**: Response chunk
  ```json
  {"chunk": "The weather in London is..."}
  ```

- **done**: Processing completed
  ```json
  {"status": "completed", "agent": "weather", "thread_id": "session_id"}
  ```

- **error**: Error occurred
  ```json
  {"error": "Error message"}
  ```

## Testing

### Using the Test Script

Run the provided test script:
```bash
python test_api.py
```

This will test all endpoints including streaming.

### Using cURL

**Health Check:**
```bash
curl http://127.0.0.1:8000/health
```

**List Agents:**
```bash
curl http://127.0.0.1:8000/agents
```

**Chat (Non-Streaming):**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List files", "thread_id": "test1"}'
```

**Stream Chat (SSE):**
```bash
curl -X POST http://127.0.0.1:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather?", "thread_id": "test2"}' \
  -N
```

### Using Python Requests

**Non-Streaming Example:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={
        "message": "Search for information about LangGraph",
        "thread_id": "my_session"
    }
)
print(response.json())
```

**Streaming Example:**
```python
import requests
import json
import sseclient

response = requests.post(
    "http://127.0.0.1:8000/stream",
    json={
        "message": "What's the weather in Paris?",
        "thread_id": "my_session"
    },
    stream=True
)

client = sseclient.SSEClient(response)
for event in client.events():
    if event.event == "message":
        data = json.loads(event.data)
        print(data['chunk'], end="", flush=True)
    elif event.event == "done":
        print("\n✓ Done")
        break
```

## Thread Management

The API supports conversation threads using `thread_id`. Messages with the same `thread_id` will maintain conversation context and history.

Example:
```python
# First message
response1 = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"message": "Create a file called test.txt", "thread_id": "session1"}
)

# Follow-up message (remembers context)
response2 = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"message": "Now add 'Hello World' to it", "thread_id": "session1"}
)
```

## Available Agents

1. **File Operations Agent**: Handles file system operations (read, write, list, move files)
2. **Research Agent**: Performs web searches and information gathering
3. **Weather Agent**: Provides weather information using MCP server integration

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (e.g., empty message)
- `500`: Internal server error

Error responses include details:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Development

For development with auto-reload:
```bash
uvicorn api_server:app --reload --host 127.0.0.1 --port 8000
```

## CORS Configuration

The server allows all origins by default. To restrict origins in production, modify the CORS settings in `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Deployment

For production deployment:

1. Use a production ASGI server
2. Set up proper environment variables
3. Configure CORS for specific origins
4. Add authentication/authorization
5. Set up logging and monitoring

Example production command:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```
