# 🧠 Engram — AI-Powered Second Brain

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> A multimodal AI-powered second brain that ingests, processes, and connects knowledge from text, PDFs, images, videos, and chat exports. Features hybrid retrieval, knowledge graphs, and RAG-powered conversations with sub-100ms retrieval times.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd engram
cp .env.example .env
# Edit .env with your configuration
```

2. **Run with Docker (Recommended):**
```bash
make docker-up
```

3. **Or run locally:**
```bash
make venv
make install
make migrate
make seed
make run
```

The API will be available at:
- **API**: http://localhost:8000
- **OpenAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/v1/health
- **Graph Visualization**: http://localhost:8000/graph
- **RQ Dashboard**: http://localhost:9181

## 🧠 Second Brain Features

### 🔄 Multimodal Ingestion
- **Web Content**: Extract and chunk articles, blogs, documentation
- **PDFs**: Process documents with text extraction and chunking
- **Images**: Extract embeddings using CLIP, generate captions
- **Videos**: Transcribe with Whisper, extract keyframes
- **Chat Exports**: Import from Slack, Discord, or custom JSON formats
- **Background Processing**: Async job queue with RQ for heavy processing

### 🕸️ Knowledge Graph
- **Entity Extraction**: Automatic NER with spaCy
- **Relationship Mining**: Pattern-based and co-occurrence analysis
- **Graph Visualization**: Interactive D3.js force-directed layout
- **Subgraph Queries**: Explore connections around entities

### 💬 RAG-Powered Chat
- **Hybrid Retrieval**: Search across all modalities simultaneously
- **Memory Context**: Ground responses in your personal knowledge
- **Conversation Memory**: Store and reference past conversations
- **Modality-Aware**: Respect content types in retrieval
- **Router Proxy**: Drop-in LLM completion with automatic memory injection

### ⚡ Performance & Features
- **Sub-100ms Retrieval**: Optimized vector search with ranking
- **Multi-tenant**: Isolated knowledge spaces per user/organization
- **Scalable**: PostgreSQL + ChromaDB/Pinecone backend
- **API Keys**: Secure authentication with scoped permissions
- **Analytics**: Request logging and performance monitoring
- **Connectors**: Sync with Google Drive, Notion, Slack
- **Smart Forgetting**: Automatic cleanup of low-importance memories

## 📖 Usage Examples

### Multimodal Ingestion

```python
import requests

# Ingest web content
response = requests.post("http://localhost:8000/v1/ingest/url", json={
    "tenant_id": "my-tenant",
    "user_id": "my-user", 
    "url": "https://example.com/article",
    "type": "web"
})

# Ingest PDF file
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "tenant_id": "my-tenant",
        "user_id": "my-user",
        "type": "pdf"
    }
    response = requests.post("http://localhost:8000/v1/ingest/file", files=files, data=data)

# Ingest chat export
response = requests.post("http://localhost:8000/v1/ingest/chat", json={
    "tenant_id": "my-tenant",
    "user_id": "my-user",
    "platform": "slack",
    "items": [
        {"text": "Meeting at 3pm", "author": "john", "timestamp": "2024-01-01T15:00:00Z"},
        {"text": "Sounds good!", "author": "jane", "timestamp": "2024-01-01T15:01:00Z"}
    ]
})
```

### Knowledge Graph Exploration

```python
# Search for entities
response = requests.get("http://localhost:8000/v1/graph/search", params={
    "tenant_id": "my-tenant",
    "user_id": "my-user",
    "entity": "John"
})

# Get subgraph around an entity
response = requests.get("http://localhost:8000/v1/graph/subgraph", params={
    "tenant_id": "my-tenant", 
    "user_id": "my-user",
    "seed_label": "Apple Inc",
    "radius": 2
})

# Get graph statistics
response = requests.get("http://localhost:8000/v1/graph/stats", params={
    "tenant_id": "my-tenant",
    "user_id": "my-user"
})
```

### RAG-Powered Chat

```python
# Chat with your memories
response = requests.post("http://localhost:8000/v1/chat/", json={
    "tenant_id": "my-tenant",
    "user_id": "my-user",
    "messages": [
        {"role": "user", "content": "What do I know about machine learning?"}
    ],
    "retrieval_hints": {
        "modalities": ["text", "pdf", "web"],
        "k": 10
    }
})

print(response.json()["message"]["content"])
```

### Using the SDKs

#### Python SDK

```python
from engram_client import EngramClient

client = EngramClient(
    api_key="your-api-key",
    base_url="http://localhost:8000"
)

# Store a memory
memory = await client.upsert(
    tenant_id="my-tenant",
    user_id="my-user", 
    text="I learned about machine learning today",
    importance=0.8
)

# Chat with memories
response = await client.chat(
    tenant_id="my-tenant",
    user_id="my-user",
    messages=[{"role": "user", "content": "What did I learn?"}]
)

# Explore knowledge graph
graph = await client.graph_subgraph(
    tenant_id="my-tenant",
    user_id="my-user",
    seed_label="machine learning"
)
```

#### TypeScript SDK

```typescript
import EngramClient from 'engram-sdk';

const client = new EngramClient(
  'your-api-key',
  'http://localhost:8000'
);

// Store a memory
const memory = await client.upsert(
  'my-tenant',
  'my-user',
  'I learned about machine learning today',
  { topic: 'ai' },
  0.8
);

// Chat with memories
const response = await client.chat(
  'my-tenant',
  'my-user',
  [{ role: 'user', content: 'What did I learn?' }]
);
```

### Basic Memory Operations

```python
import requests

# Create a tenant
tenant = requests.post("http://localhost:8000/v1/tenants", 
                      json={"name": "my-app"}).json()

# Store memories
requests.post("http://localhost:8000/v1/memories/upsert", json={
    "tenant_id": tenant["id"],
    "user_id": "user123",
    "texts": [
        "User prefers dark mode in applications",
        "User is interested in machine learning and AI"
    ],
    "metadata": [{"source": "preferences"}, {"source": "interests"}]
})

# Retrieve relevant memories
memories = requests.post("http://localhost:8000/v1/memories/retrieve", json={
    "tenant_id": tenant["id"],
    "user_id": "user123",
    "query": "What does the user like?",
    "top_k": 5
}).json()

print(memories)
```

### Context Injection

```python
# Get context-injected prompt for LLM
response = requests.post("http://localhost:8000/v1/context/inject", json={
    "tenant_id": tenant["id"],
    "user_id": "user123",
    "query": "User preferences",
    "prompt": "Based on the user's preferences, suggest a new feature.",
    "max_memories": 3
}).json()

print(response["injected_prompt"])
```

## 🏗️ Architecture

Engram provides a clean separation between providers, storage backends, and business logic:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI API   │───▶│  Core Services  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Middleware    │    │   Vector Store  │
                       │ (Rate Limit,    │    │  (Chroma/Pine   │
                       │  Request ID)    │    │     cone)       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Embeddings    │
                       │   (Metadata)    │    │  (Local/Cloud)  │
                       └─────────────────┘    └─────────────────┘
```

### Key Components

- **Core Services**: Memory storage, retrieval, and consolidation logic
- **Provider Layer**: Pluggable embeddings and LLM providers (OpenAI, Anthropic, Google, Local)
- **Vector Storage**: ChromaDB (default) or Pinecone for semantic search
- **Relational Storage**: PostgreSQL for metadata and tenant management
- **API Layer**: RESTful FastAPI with automatic OpenAPI documentation

## 🔧 Configuration

Key environment variables (see `.env.example`):

```bash
# API Configuration
APP_ENV=local
LOG_LEVEL=INFO
PORT=8000

# Embeddings Provider
DEFAULT_EMBEDDINGS_PROVIDER=local  # or openai, anthropic, google

# Vector Database
VECTOR_BACKEND=chroma  # or pinecone
CHROMA_PERSIST_DIR=/data/chroma

# Database
POSTGRES_HOST=localhost
POSTGRES_DB=engram
POSTGRES_USER=engram
POSTGRES_PASSWORD=engram

# Retrieval Tuning
RANK_ALPHA=0.70    # Cosine similarity weight
RANK_BETA=0.20     # Recency boost weight  
RANK_GAMMA=0.15    # Importance weight
RANK_DELTA=0.05    # Decay penalty weight
RECENCY_TAU_DAYS=14
```

## 🧪 Development

### Setup Development Environment

```bash
make venv          # Create virtual environment
make install       # Install dependencies
make migrate       # Run database migrations
make smoke-second-brain  # Test all second brain functionality
make seed          # Load demo data
make test          # Run tests with coverage
make lint          # Run linters
make fmt           # Format code
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=engram --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality

Pre-commit hooks are configured for:
- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

## 📊 Performance

- **Retrieval**: <100ms p95 with warm cache
- **Embeddings**: Cached sentence-transformers model
- **Storage**: Efficient vector indexing with ChromaDB
- **Memory**: Configurable limits and LRU eviction

## 🔒 Security & Multi-tenancy

- **Tenant Isolation**: All operations scoped to tenant_id + user_id
- **Rate Limiting**: Token bucket implementation with Redis
- **Input Validation**: Pydantic v2 models with strict validation
- **Error Handling**: Sanitized error responses with request tracing

## 📚 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/tenants` | Create tenant |
| `GET` | `/v1/tenants/{id}` | Get tenant info |
| `POST` | `/v1/memories/upsert` | Store/update memories |
| `POST` | `/v1/memories/retrieve` | Retrieve relevant memories |
| `POST` | `/v1/context/inject` | Get context-injected prompt |
| `GET` | `/v1/admin/memories` | List memories (admin) |
| `DELETE` | `/v1/admin/memories/{id}` | Delete memory (admin) |

### Second Brain Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/ingest/url` | Ingest content from URL |
| `POST` | `/v1/ingest/file` | Ingest uploaded file |
| `POST` | `/v1/ingest/chat` | Ingest chat messages |
| `GET` | `/v1/processing/status` | Get job processing status |
| `POST` | `/v1/chat` | Chat with memories |
| `POST` | `/v1/router/complete` | Router proxy completion |
| `GET` | `/v1/graph/subgraph` | Get knowledge graph subgraph |
| `GET` | `/v1/graph/search` | Search graph entities |
| `GET` | `/graph` | Graph visualization page |
| `GET` | `/v1/analytics/overview` | Get analytics overview |
| `POST` | `/v1/connectors/sync` | Sync external connector |

See `/docs` endpoint for interactive API documentation.

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Scale API instances
docker-compose up --scale api=3 -d
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/v1/health

# Check all services
docker-compose ps
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run quality checks: `make lint test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Port 8000 already in use:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
```

**Database connection issues:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Reset database
make docker-down
make docker-up
```

**ChromaDB persistence issues:**
```bash
# Clear ChromaDB data
rm -rf /data/chroma
docker-compose restart
```

### Getting Help

- Check the [API documentation](http://localhost:8000/docs)
- Review [architecture documentation](docs/architecture.md)
- Open an issue with logs and configuration details

---

Built with ❤️ for the AI community. Star ⭐ if you find this useful!
