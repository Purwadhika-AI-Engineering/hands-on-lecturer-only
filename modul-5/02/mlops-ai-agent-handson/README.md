# LLM Agent Service

A simple, modular LLM Agent service built with LangChain and FastAPI, designed for easy deployment using Docker containers.

## Features

- 🤖 **LangChain Agent**: Conversational AI agent with tools for calculations and text analysis
- 🚀 **FastAPI**: Modern, fast web framework for building APIs
- 🐳 **Docker Support**: Easy containerization and deployment
- 💬 **Chat Interface**: RESTful API for interacting with the agent
- 📝 **Memory**: Conversation history tracking
- 🔧 **Modular Design**: Clean separation between agent logic and API layer

## Project Structure

```
mlops-ai-agent-handson/
├── app.py              # FastAPI application
├── agent.py            # LangChain agent implementation
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── .dockerignore       # Docker ignore file
└── README.md          # This file
```

## Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- OpenAI API key

## Local Development Setup

### 1. Clone and Navigate to Project

```bash
cd /path/to/mlops-ai-agent-handson
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or create a `.env` file:
```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 5. Run the Application

```bash
python app.py
```

The service will be available at `http://localhost:8000`

## Docker Deployment

### 1. Build the Docker Image

```bash
docker build -t llm-agent-service .
```

### 2. Run the Container

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY="your-openai-api-key-here" llm-agent-service
```

### 3. Run in Background (Detached Mode)

```bash
docker run -d -p 8000:8000 -e OPENAI_API_KEY="your-openai-api-key-here" --name llm-agent llm-agent-service
```

### 4. View Container Logs

```bash
docker logs llm-agent
```

### 5. Stop the Container

```bash
docker stop llm-agent
```

## API Endpoints

### Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with service information |
| GET | `/health` | Health check endpoint |
| POST | `/chat` | Send a message to the agent |
| GET | `/history` | Get conversation history |
| POST | `/reset` | Reset conversation history |

## Usage Examples

### 1. Check Service Health

```bash
curl http://localhost:8000/health
```

### 2. Chat with the Agent

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello! Can you calculate 15 * 23 for me?"}'
```

### 3. Get Conversation History

```bash
curl http://localhost:8000/history
```

### 4. Reset Conversation

```bash
curl -X POST http://localhost:8000/reset
```

## Cloud Deployment

### AWS ECS/Fargate

1. **Build and push to ECR:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name llm-agent-service

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t llm-agent-service .
docker tag llm-agent-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-agent-service:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-agent-service:latest
```

2. **Create ECS Task Definition** with environment variable `OPENAI_API_KEY`

3. **Deploy to ECS Service** with Application Load Balancer

### Google Cloud Run

1. **Build and push to GCR:**
```bash
# Set project ID
export PROJECT_ID=your-project-id

# Build and push
docker build -t gcr.io/$PROJECT_ID/llm-agent-service .
docker push gcr.io/$PROJECT_ID/llm-agent-service
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy llm-agent-service \
  --image gcr.io/$PROJECT_ID/llm-agent-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-api-key
```

### Azure Container Instances

1. **Build and push to ACR:**
```bash
# Login to Azure
az login

# Create resource group and ACR
az group create --name myResourceGroup --location eastus
az acr create --resource-group myResourceGroup --name myacr --sku Basic

# Build and push
az acr build --registry myacr --image llm-agent-service:latest .
```

2. **Deploy to Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name llm-agent \
  --image myacr.azurecr.io/llm-agent-service:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server myacr.azurecr.io \
  --registry-username myacr \
  --registry-password <password> \
  --environment-variables OPENAI_API_KEY=your-api-key \
  --ports 8000
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | Yes |
| `PORT` | Port for the service (default: 8000) | No |

## Troubleshooting

### Common Issues

1. **Agent not initialized**: Check that `OPENAI_API_KEY` is set correctly
2. **Port already in use**: Change the port in the Docker run command or app.py
3. **Memory issues**: Increase Docker memory allocation
4. **API rate limits**: Check OpenAI API usage and limits

### Logs

View application logs:
```bash
# Docker logs
docker logs llm-agent

# Local development
# Logs will appear in the terminal where you run python app.py
```

## Development

### Adding New Tools

To add new tools to the agent, modify the `tools` list in `agent.py`:

```python
Tool(
    name="Your Tool Name",
    description="Description of what the tool does",
    func=your_function
)
```

### Customizing the Agent

- Modify `agent.py` to change agent behavior
- Update `app.py` to add new API endpoints
- Adjust `requirements.txt` for additional dependencies

## License

This project is for educational purposes as part of the MLOps AI Agent hands-on tutorial.

## Catatan perubahan (hands-on Docker, Nov 2026)

- `agent.py` memakai `ChatOpenAI`; model dipilih lewat env `OPENAI_MODEL` (default `gpt-4.1-mini`), misalnya `docker run -e OPENAI_MODEL=<model> ...`. Model completion lama `gpt-3.5-turbo-instruct` sudah dimatikan OpenAI.
- `requirements.txt`: `langchain-community` dan `langchain-core` di-pin agar `import` berhasil.
- `Dockerfile`: `curl` dipasang untuk HEALTHCHECK.
