# 🧠 Engram Second Brain Documentation

## Overview

Engram Second Brain is a multimodal AI-powered knowledge management system that transforms your personal and professional content into an intelligent, searchable, and interconnected knowledge base. It combines advanced AI techniques with intuitive interfaces to create a truly personalized second brain.

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingestion     │    │   Processing    │    │   Retrieval     │
│   Pipeline      │───▶│   & Storage     │───▶│   & Chat        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  • Web Scraper  │    │  • Embeddings   │    │  • Hybrid       │
│  • PDF Parser   │    │  • Graph Build  │    │    Retrieval    │
│  • Image OCR    │    │  • Vector Store │    │  • RAG Chat     │
│  • Video Trans  │    │  • Graph Store  │    │  • Visualization│
│  • Chat Import  │    │  • Metadata     │    │  • API Endpoints│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Ingestion**: Content is ingested through various pipelines (web, PDF, image, video, chat)
2. **Processing**: Content is chunked, embedded, and processed for graph extraction
3. **Storage**: Processed content is stored in vector database and graph database
4. **Retrieval**: Hybrid retrieval combines semantic search with graph traversal
5. **Chat**: RAG-powered conversations ground responses in retrieved knowledge

## 🔄 Multimodal Ingestion

### Supported Content Types

| Modality | Description | Extraction Method | Embedding Model |
|----------|-------------|-------------------|-----------------|
| **Web** | Articles, blogs, documentation | trafilatura, BeautifulSoup | Sentence Transformers |
| **PDF** | Documents, papers, reports | PyMuPDF, pdfplumber | Sentence Transformers |
| **Image** | Photos, screenshots, diagrams | CLIP, OCR (future) | CLIP/SigLIP |
| **Video** | Recordings, tutorials | Whisper + keyframes | Sentence Transformers + CLIP |
| **Chat** | Slack, Discord, exports | JSON parsing | Sentence Transformers |
| **Text** | Raw text content | Direct processing | Sentence Transformers |

### Ingestion Pipeline

```python
# Example: Ingesting a PDF document
POST /v1/ingest/file
{
    "tenant_id": "user-123",
    "user_id": "john-doe",
    "type": "pdf",
    "file": <binary_data>
}

# Response
{
    "status": "success",
    "memory_ids": ["mem_abc123", "mem_def456"],
    "chunks_created": 15,
    "graph_nodes_created": 8,
    "graph_edges_created": 12,
    "metadata": {
        "modality": "pdf",
        "source_uri": "document.pdf",
        "embedding_dim": 384,
        "embedding_provider": "sentence-transformers-all-MiniLM-L6-v2"
    }
}
```

### Chunking Strategy

- **Text Chunks**: 512 tokens with 76 token overlap (15%)
- **Image Chunks**: Single image per chunk with optional caption
- **Video Chunks**: Transcript chunks + keyframe images every 8 seconds
- **Chat Chunks**: Message groups by conversation context

## 🕸️ Knowledge Graph

### Entity Extraction

The system automatically extracts entities from all text content using:

- **spaCy NER**: Named Entity Recognition for persons, organizations, locations, etc.
- **Custom Patterns**: Domain-specific entity extraction patterns
- **Co-occurrence Analysis**: Entities that appear together in similar contexts

### Relationship Mining

Relationships are discovered through:

1. **Pattern-based Extraction**: Regex patterns for common relationship types
   - `(Person) works for (Organization)`
   - `(Organization) founded by (Person)`
   - `(Product) built with (Technology)`

2. **Co-occurrence Analysis**: Entities that frequently appear together
3. **Semantic Similarity**: Entities with similar embedding vectors

### Graph Structure

```python
# Node Structure
{
    "id": "entity_hash",
    "label": "Apple Inc",
    "type": "organization",
    "properties": {
        "original_type": "ORG",
        "confidence": 0.95,
        "modality": "web",
        "source_count": 5
    }
}

# Edge Structure
{
    "src": "entity_1",
    "dst": "entity_2", 
    "relation": "founded_by",
    "weight": 1.0,
    "properties": {
        "head_type": "ORG",
        "tail_type": "PERSON",
        "modality": "pdf",
        "confidence": 0.8
    }
}
```

### Graph Queries

```python
# Subgraph around an entity
GET /v1/graph/subgraph?tenant_id=user-123&user_id=john&seed_label=Apple Inc&radius=2

# Entity search
GET /v1/graph/search?tenant_id=user-123&user_id=john&entity=Steve Jobs

# Graph statistics
GET /v1/graph/stats?tenant_id=user-123&user_id=john
```

## 💬 RAG-Powered Chat

### Hybrid Retrieval

The chat system uses a sophisticated hybrid retrieval approach:

1. **Semantic Search**: Query embeddings matched against all content embeddings
2. **Graph Traversal**: Related entities discovered through graph connections
3. **Modality Filtering**: Respect user preferences for content types
4. **Late Fusion**: Combine results from different retrieval methods

### Retrieval Process

```python
# Chat Request
POST /v1/chat/
{
    "tenant_id": "user-123",
    "user_id": "john-doe",
    "messages": [
        {"role": "user", "content": "What do I know about machine learning?"}
    ],
    "retrieval_hints": {
        "modalities": ["text", "pdf", "web"],
        "k": 10
    }
}

# Retrieval Pipeline
1. Generate query embedding
2. Search vector database for relevant memories
3. Filter by modality preferences
4. Rank by composite score (similarity + recency + importance)
5. Build memory context
6. Generate response with LLM
```

### Memory Context Format

```
[MEMORY CONTEXT START]
- PDF: Machine learning is a subset of artificial intelligence (Source: ml_guide.pdf)
- WEB: Deep learning uses neural networks with multiple layers (Source: https://example.com/dl-intro)
- CHAT: Discussed ML algorithms in team meeting (Source: slack_export.json)
[MEMORY CONTEXT END]
```

### Response Generation

The system uses configured LLM providers (OpenAI, Anthropic, Google) to generate responses grounded in the retrieved memories. The prompt includes:

- System instructions for using memory context
- Retrieved memories formatted as context
- Conversation history
- User's current question

## ⚡ Performance Optimization

### Vector Search

- **Indexing**: HNSW (Hierarchical Navigable Small World) for fast approximate search
- **Quantization**: 8-bit quantization for memory efficiency
- **Batch Processing**: Efficient batch embedding generation

### Graph Operations

- **Indexing**: Database indexes on entity labels, types, and relationships
- **Caching**: Frequently accessed subgraphs cached in Redis
- **Lazy Loading**: Load graph components on-demand

### Retrieval Ranking

The composite ranking score combines multiple signals:

```
score = α × similarity + β × recency + γ × importance - δ × decay
```

Where:
- **α = 0.70**: Semantic similarity weight
- **β = 0.20**: Recency boost (recently accessed content)
- **γ = 0.15**: Importance weight (user-assigned or computed)
- **δ = 0.05**: Decay penalty (older content)

## 🔧 Configuration

### Environment Variables

```bash
# Multimodal Configuration
DEFAULT_IMAGE_EMBEDDINGS=clip           # or siglip
WHISPER_MODEL=small                     # for faster-whisper
KEYFRAME_SEC=8                          # ffmpeg keyframe interval
BLOB_STORE_DIR=/data/blobs              # file storage directory

# Graph Configuration
GRAPH_TRIPLE_EXTRACTION=heuristic       # llm|heuristic
GRAPH_MAX_RADIUS=2                      # max graph traversal depth
SPACY_MODEL=en_core_web_sm             # spaCy model name

# Chat Configuration
CHAT_CONTEXT_WINDOW=4000               # max context tokens
CHAT_MAX_MEMORIES=10                   # max memories per query
CHAT_TEMPERATURE=0.7                   # LLM temperature
```

### Provider Configuration

```bash
# Embedding Providers
OPENAI_API_KEY=sk-...                  # OpenAI embeddings
ANTHROPIC_API_KEY=sk-ant-...           # Anthropic LLM
GOOGLE_APPLICATION_CREDENTIALS=...     # Google Vertex AI

# Vector Database
VECTOR_BACKEND=chroma                  # chroma|pinecone
CHROMA_PERSIST_DIR=/data/chroma        # ChromaDB storage
PINECONE_API_KEY=...                   # Pinecone API key
```

## 🧪 Testing

### Smoke Test

Run the comprehensive smoke test to verify all functionality:

```bash
make smoke-second-brain
```

This test covers:
- ✅ API health check
- ✅ Web content ingestion
- ✅ Chat content ingestion  
- ✅ Graph search and subgraph queries
- ✅ RAG-powered chat
- ✅ Graph statistics

### Unit Tests

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/test_ingest_pdf.py
pytest tests/test_ingest_web.py
pytest tests/test_chat_rag.py
pytest tests/test_graph_layer.py
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Services included:
# - PostgreSQL (metadata storage)
# - Redis (caching and queues)
# - ChromaDB (vector storage)
# - Engram API (main service)
# - Migration service (database setup)
```

### Production Considerations

1. **Scalability**: Use Pinecone for vector storage at scale
2. **Security**: Implement authentication and authorization
3. **Monitoring**: Add metrics and logging
4. **Backup**: Regular database and vector store backups
5. **Performance**: Tune embedding models and retrieval parameters

## 🔮 Future Enhancements

### Planned Features

- **Audio Processing**: Direct audio file ingestion and transcription
- **OCR Integration**: Extract text from images and scanned documents
- **Multi-language Support**: Support for non-English content
- **Advanced Graph Analytics**: Graph algorithms for insights
- **Collaborative Features**: Shared knowledge spaces
- **Mobile App**: Native mobile interface
- **API Integrations**: Connect with external knowledge sources

### Extensibility

The system is designed for easy extension:

- **Custom Extractors**: Add new content type processors
- **Custom Embeddings**: Integrate domain-specific models
- **Custom Graph Patterns**: Add specialized relationship patterns
- **Custom LLM Providers**: Support additional language models

## 📚 API Reference

### Ingestion Endpoints

- `POST /v1/ingest/url` - Ingest content from URL
- `POST /v1/ingest/file` - Ingest uploaded file
- `POST /v1/ingest/chat` - Ingest chat export

### Graph Endpoints

- `GET /v1/graph/search` - Search entities
- `GET /v1/graph/subgraph` - Get subgraph around entity
- `GET /v1/graph/stats` - Get graph statistics
- `GET /v1/graph/` - Graph visualization interface

### Chat Endpoints

- `POST /v1/chat/` - RAG-powered chat

### Core Endpoints

- `GET /v1/health` - Health check
- `GET /v1/stats` - System statistics
- `POST /v1/memories` - Create memory
- `GET /v1/memories` - Retrieve memories

For complete API documentation, visit `/docs` when running the service.
