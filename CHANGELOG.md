# Changelog

All notable changes to Engram will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Engram - Universal Memory Layer for LLMs
- Multi-tenant memory storage with PostgreSQL
- Semantic memory retrieval with vector databases (ChromaDB, Pinecone)
- Provider-agnostic embeddings (Local, OpenAI, Google)
- Memory consolidation and forgetting policies
- REST API with FastAPI
- Docker and docker-compose support
- Comprehensive test suite with 80%+ coverage
- CI/CD pipeline with GitHub Actions
- Complete documentation and examples

### Features
- **Memory Management**
  - Store, retrieve, and delete memories
  - Batch operations for efficiency
  - Text truncation with metadata preservation
  - Soft delete with background cleanup
  
- **Semantic Search**
  - Vector-based similarity search
  - Composite scoring with recency and importance
  - Configurable ranking weights
  - Sub-100ms retrieval performance
  
- **Multi-Provider Support**
  - Local sentence-transformers embeddings
  - OpenAI embeddings and LLM integration
  - Google Vertex AI support
  - Anthropic Claude integration
  - Easy provider switching via configuration
  
- **Memory Consolidation**
  - Automatic duplicate detection
  - Intelligent memory merging
  - Configurable forgetting policies
  - Background cleanup processes
  
- **API Features**
  - RESTful API with OpenAPI documentation
  - Context injection for LLM prompts
  - Admin endpoints for memory management
  - Rate limiting and request tracing
  - Health checks and monitoring
  
- **Developer Experience**
  - Comprehensive examples and demos
  - Local development setup
  - Pre-commit hooks for code quality
  - Makefile for common tasks
  - Docker development environment

### Technical Details
- **Backend**: Python 3.11, FastAPI, Pydantic v2
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Vector Storage**: ChromaDB (default), Pinecone (optional)
- **Caching**: Redis for rate limiting and session storage
- **Testing**: pytest with 80%+ coverage
- **Code Quality**: ruff, black, isort, mypy
- **CI/CD**: GitHub Actions with multi-stage pipeline

### Documentation
- Complete API reference
- Architecture documentation
- Contributing guidelines
- Example scripts and tutorials
- Docker deployment guide

## [0.1.0] - 2024-01-01

### Added
- Initial public release
- Core memory storage and retrieval functionality
- Multi-tenant architecture
- Provider abstraction layer
- Comprehensive test suite
- Docker deployment support
- CI/CD pipeline
- Complete documentation

---

## Release Notes

### v0.1.0 - Initial Release

This is the first public release of Engram, a universal memory layer for LLM applications.

**Key Features:**
- 🧠 **Semantic Memory Storage**: Store and retrieve memories using vector similarity
- 🔄 **Multi-Provider Support**: Switch between local and cloud embeddings/LLMs
- 🏢 **Multi-Tenant Architecture**: Complete isolation between tenants and users
- ⚡ **High Performance**: Sub-100ms retrieval with configurable ranking
- 🔧 **Easy Integration**: REST API with comprehensive documentation
- 🐳 **Docker Ready**: Full containerization with docker-compose
- 📊 **Production Ready**: Monitoring, logging, and error handling

**Getting Started:**
```bash
# Clone and setup
git clone https://github.com/your-org/engram.git
cd engram
cp env.example .env

# Run with Docker
make docker-up

# Or run locally
make venv
make install
make migrate
make run
```

**API Usage:**
```python
import httpx

# Create tenant
tenant = httpx.post("http://localhost:8000/v1/tenants", 
                   json={"name": "my-app"}).json()

# Store memories
httpx.post("http://localhost:8000/v1/memories/upsert", json={
    "tenant_id": tenant["id"],
    "user_id": "user123",
    "texts": ["User prefers dark mode"]
})

# Retrieve memories
memories = httpx.post("http://localhost:8000/v1/memories/retrieve", json={
    "tenant_id": tenant["id"],
    "user_id": "user123",
    "query": "What does the user prefer?"
}).json()
```

**What's Next:**
- Advanced consolidation algorithms
- Real-time WebSocket updates
- GraphQL API support
- Analytics dashboard
- Enterprise features (SSO, RBAC)

For more information, visit our [documentation](docs/) or check out the [examples](examples/).

