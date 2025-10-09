# Engram API Reference

## Base URL

```
http://localhost:8000/v1
```

## Authentication

Currently, Engram uses API key-based authentication. Include your API key in the request headers:

```http
Authorization: Bearer YOUR_API_KEY
```

## Content Type

All requests and responses use JSON:

```http
Content-Type: application/json
Accept: application/json
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "request_id": "uuid4-request-id",
  "timestamp": 1640995200.0
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Endpoints

### Health Check

Check service health and status.

```http
GET /v1/health
```

**Response:**
```json
{
  "status": "ok",
  "uptime_seconds": 3600.5,
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### Tenants

#### Create Tenant

Create a new tenant for multi-tenant isolation.

```http
POST /v1/tenants
```

**Request Body:**
```json
{
  "name": "my-application"
}
```

**Response:**
```json
{
  "id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
  "name": "my-application",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Validation:**
- `name`: Required, 1-255 characters, unique

#### Get Tenant

Retrieve tenant information.

```http
GET /v1/tenants/{tenant_id}
```

**Response:**
```json
{
  "id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
  "name": "my-application",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Memories

#### Upsert Memories

Store or update memories for a user. Supports batch operations.

```http
POST /v1/memories/upsert
```

**Request Body:**
```json
{
  "tenant_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
  "user_id": "user123",
  "texts": [
    "User prefers dark mode in applications",
    "User is interested in machine learning and AI",
    "User works as a software engineer at a tech company"
  ],
  "metadata": [
    {
      "category": "preferences",
      "source": "ui_settings"
    },
    {
      "category": "interests",
      "source": "profile"
    },
    {
      "category": "work",
      "source": "bio"
    }
  ],
  "importance": [0.8, 0.9, 0.7]
}
```

**Response:**
```json
{
  "message": "Successfully upserted 3 memories",
  "memory_ids": [
    "01HK8X9Y2Z3A4B5C6D7E8F9G0I",
    "01HK8X9Y2Z3A4B5C6D7E8F9G0J",
    "01HK8X9Y2Z3A4B5C6D7E8F9G0K"
  ],
  "count": 3
}
```

**Validation:**
- `tenant_id`: Required, valid ULID
- `user_id`: Required, valid ULID
- `texts`: Required, 1-100 items, each 1-2048 characters
- `metadata`: Optional, same length as texts
- `importance`: Optional, same length as texts, 0.0-1.0

#### Retrieve Memories

Retrieve semantically relevant memories for a query.

```http
POST /v1/memories/retrieve
```

**Request Body:**
```json
{
  "tenant_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
  "user_id": "user123",
  "query": "What does the user prefer?",
  "top_k": 5
}
```

**Response:**
```json
[
  {
    "memory_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0I",
    "text": "User prefers dark mode in applications",
    "score": 0.95,
    "metadata": {
      "category": "preferences",
      "source": "ui_settings"
    },
    "importance": 0.8,
    "created_at": "2024-01-01T00:00:00Z",
    "last_accessed_at": "2024-01-01T12:00:00Z"
  },
  {
    "memory_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0J",
    "text": "User is interested in machine learning and AI",
    "score": 0.87,
    "metadata": {
      "category": "interests",
      "source": "profile"
    },
    "importance": 0.9,
    "created_at": "2024-01-01T00:00:00Z",
    "last_accessed_at": "2024-01-01T12:00:00Z"
  }
]
```

**Validation:**
- `tenant_id`: Required, valid ULID
- `user_id`: Required, valid ULID
- `query`: Required, 1-1000 characters
- `top_k`: Optional, 1-100, default 12

**Scoring:**
Memories are ranked using a composite score:
- Cosine similarity with query embedding
- Recency boost (more recent = higher score)
- Importance weight from metadata
- Decay penalty for old memories

---

### Context Injection

Inject relevant memories into a prompt for LLM applications.

```http
POST /v1/context/inject
```

**Request Body:**
```json
{
  "tenant_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
  "user_id": "user123",
  "query": "user preferences",
  "prompt": "Based on the user's preferences, suggest a new feature for our app.",
  "max_memories": 3
}
```

**Response:**
```json
{
  "injected_prompt": "[MEMORY CONTEXT START]\n- User prefers dark mode in applications\n- User is interested in machine learning and AI\n- User works as a software engineer at a tech company\n[MEMORY CONTEXT END]\n\nBased on the user's preferences, suggest a new feature for our app.",
  "memories_used": [
    {
      "memory_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0I",
      "text": "User prefers dark mode in applications",
      "score": 0.95,
      "metadata": {
        "category": "preferences",
        "source": "ui_settings"
      },
      "importance": 0.8,
      "created_at": "2024-01-01T00:00:00Z",
      "last_accessed_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

**Validation:**
- `tenant_id`: Required, valid ULID
- `user_id`: Required, valid ULID
- `query`: Required, 1-1000 characters
- `prompt`: Required, non-empty
- `max_memories`: Optional, 1-20, default 6
- `provider`: Optional, LLM provider name

---

### Admin Endpoints

#### List Memories

List memories with pagination (admin only).

```http
GET /v1/admin/memories
```

**Query Parameters:**
- `tenant_id`: Required, tenant ID
- `user_id`: Optional, user ID filter
- `limit`: Optional, 1-1000, default 100
- `offset`: Optional, ≥0, default 0
- `active_only`: Optional, boolean, default true

**Response:**
```json
{
  "memories": [
    {
      "memory_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0I",
      "text": "User prefers dark mode in applications",
      "score": 0.0,
      "metadata": {
        "category": "preferences",
        "source": "ui_settings"
      },
      "importance": 0.8,
      "created_at": "2024-01-01T00:00:00Z",
      "last_accessed_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total_count": 150,
  "limit": 100,
  "offset": 0
}
```

#### Delete Memory

Soft delete a memory (admin only).

```http
DELETE /v1/admin/memories/{memory_id}
```

**Query Parameters:**
- `tenant_id`: Required, tenant ID
- `user_id`: Required, user ID

**Response:**
```json
{
  "message": "Memory deleted successfully",
  "memory_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0I"
}
```

#### Get Statistics

Get service statistics (admin only).

```http
GET /v1/stats
```

**Response:**
```json
{
  "total_tenants": 5,
  "total_memories": 1000,
  "active_memories": 950,
  "vector_provider": "chromadb",
  "embeddings_provider": "local"
}
```

---

## Rate Limiting

Engram implements rate limiting to prevent abuse:

- **Default**: 60 requests per minute per client
- **Burst**: 10 requests above limit allowed
- **Headers**: Rate limit info in response headers

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995260
```

**Rate Limit Exceeded Response:**
```json
{
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "request_id": "uuid4-request-id",
  "timestamp": 1640995200.0
}
```

## Request Tracing

All requests include a unique request ID for tracing:

**Request Headers:**
```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Response Headers:**
```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

## SDK Examples

### Python

```python
import httpx

async def create_tenant(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/tenants",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

async def upsert_memories(tenant_id: str, user_id: str, texts: list[str]) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/memories/upsert",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "texts": texts
            }
        )
        response.raise_for_status()
        return response.json()

async def retrieve_memories(tenant_id: str, user_id: str, query: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/memories/retrieve",
            json={
                "tenant_id": tenant_id,
                "user_id": user_id,
                "query": query,
                "top_k": 5
            }
        )
        response.raise_for_status()
        return response.json()
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:8000/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

async function createTenant(name) {
  const response = await api.post('/tenants', { name });
  return response.data;
}

async function upsertMemories(tenantId, userId, texts) {
  const response = await api.post('/memories/upsert', {
    tenant_id: tenantId,
    user_id: userId,
    texts
  });
  return response.data;
}

async function retrieveMemories(tenantId, userId, query) {
  const response = await api.post('/memories/retrieve', {
    tenant_id: tenantId,
    user_id: userId,
    query,
    top_k: 5
  });
  return response.data;
}
```

### cURL Examples

**Create Tenant:**
```bash
curl -X POST "http://localhost:8000/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-app"}'
```

**Upsert Memories:**
```bash
curl -X POST "http://localhost:8000/v1/memories/upsert" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
    "user_id": "user123",
    "texts": ["User prefers dark mode"]
  }'
```

**Retrieve Memories:**
```bash
curl -X POST "http://localhost:8000/v1/memories/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "01HK8X9Y2Z3A4B5C6D7E8F9G0H",
    "user_id": "user123",
    "query": "user preferences"
  }'
```

## WebSocket Support (Future)

Planned WebSocket endpoints for real-time features:

- `ws://localhost:8000/v1/ws/memories` - Real-time memory updates
- `ws://localhost:8000/v1/ws/consolidation` - Consolidation progress
- `ws://localhost:8000/v1/ws/stats` - Live statistics

## GraphQL Support (Future)

Planned GraphQL endpoint for complex queries:

- `POST /v1/graphql` - GraphQL query endpoint
- Schema introspection at `/v1/graphql/schema`

This API reference covers the core functionality of Engram. For the most up-to-date documentation, visit the interactive OpenAPI docs at `/docs` when running the service locally.
