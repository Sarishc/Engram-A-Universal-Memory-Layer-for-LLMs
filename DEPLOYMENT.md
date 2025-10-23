# Engram Deployment Guide

This guide covers deploying the Engram Memory System in various environments.

## 🚀 Quick Start

### Local Development

1. **Prerequisites**
   ```bash
   # Install dependencies
   - Docker & Docker Compose
   - Python 3.11+
   - Node.js 18+
   ```

2. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd engram
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run with Docker**
   ```bash
   make docker-up
   ```

4. **Access Services**
   - **API**: http://localhost:8000
   - **Web UI**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs
   - **RQ Dashboard**: http://localhost:9181

### Production Deployment

#### Option 1: Docker Compose (Recommended for small-medium deployments)

1. **Environment Setup**
   ```bash
   # Create production environment file
   cp .env.example .env.production
   
   # Edit production settings
   nano .env.production
   ```

2. **Configure Environment Variables**
   ```bash
   # Database
   POSTGRES_PASSWORD=your-secure-password
   DATABASE_URL=postgresql://engram:your-secure-password@postgres:5432/engram
   
   # API Keys
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   
   # Security
   JWT_SECRET_KEY=your-jwt-secret
   ENCRYPTION_KEY=your-encryption-key
   
   # External Services
   REDIS_URL=redis://redis:6379/0
   VECTOR_BACKEND=chroma
   ```

3. **Deploy**
   ```bash
   # Production deployment
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   
   # Run migrations
   docker-compose exec api python -m alembic upgrade head
   
   # Create initial tenant
   docker-compose exec api python -c "
   from engram.core.memory_store import MemoryStore
   from engram.database.postgres import get_db_session
   
   with get_db_session() as db:
       store = MemoryStore(db_session=db)
       tenant = store.create_tenant('default')
       print(f'Created tenant: {tenant.id}')
   "
   ```

#### Option 2: Kubernetes (Recommended for large-scale deployments)

1. **Create Kubernetes Manifests**
   ```yaml
   # k8s/namespace.yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: engram
   ```

2. **Deploy with Helm**
   ```bash
   # Install Helm chart
   helm install engram ./helm/engram \
     --namespace engram \
     --create-namespace \
     --set postgres.auth.postgresPassword=your-password \
     --set redis.auth.enabled=false \
     --set api.openaiApiKey=your-key
   ```

3. **Configure Ingress**
   ```yaml
   # k8s/ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: engram-ingress
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
   spec:
     rules:
     - host: engram.yourdomain.com
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: engram-api
               port:
                 number: 8000
         - path: /
           pathType: Prefix
           backend:
             service:
               name: engram-web
               port:
                 number: 3000
   ```

#### Option 3: Cloud Provider Deployment

##### AWS ECS

1. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name engram-cluster
   ```

2. **Deploy with Terraform**
   ```hcl
   # terraform/main.tf
   resource "aws_ecs_cluster" "engram" {
     name = "engram-cluster"
   }
   
   resource "aws_ecs_service" "engram_api" {
     name            = "engram-api"
     cluster         = aws_ecs_cluster.engram.id
     task_definition = aws_ecs_task_definition.engram_api.arn
     desired_count   = 2
   }
   ```

##### Google Cloud Run

1. **Deploy API Service**
   ```bash
   gcloud run deploy engram-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Deploy Web UI**
   ```bash
   gcloud run deploy engram-web \
     --source ./apps/web \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

##### Azure Container Instances

1. **Deploy with Azure CLI**
   ```bash
   az container create \
     --resource-group engram-rg \
     --name engram-api \
     --image your-registry/engram-api:latest \
     --ports 8000
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Application environment | `local` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `PORT` | API server port | `8000` | No |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` | Yes |
| `POSTGRES_DB` | Database name | `engram` | Yes |
| `POSTGRES_USER` | Database user | `engram` | Yes |
| `POSTGRES_PASSWORD` | Database password | - | Yes |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | Yes |
| `VECTOR_BACKEND` | Vector database backend | `chroma` | Yes |
| `DEFAULT_EMBEDDINGS_PROVIDER` | Embeddings provider | `local` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | No |
| `JWT_SECRET_KEY` | JWT signing key | - | Yes |
| `ENCRYPTION_KEY` | Data encryption key | - | Yes |

### Database Configuration

#### PostgreSQL Setup

1. **Create Database**
   ```sql
   CREATE DATABASE engram;
   CREATE USER engram WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE engram TO engram;
   ```

2. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

#### Vector Database Options

##### ChromaDB (Default)
```bash
# Local ChromaDB
VECTOR_BACKEND=chroma
CHROMA_PERSIST_DIR=/data/chroma

# ChromaDB Cloud
VECTOR_BACKEND=chroma
CHROMA_SERVER_HOST=your-chroma-host
CHROMA_SERVER_HTTP_PORT=8000
CHROMA_SERVER_SSL_ENABLED=true
```

##### Pinecone
```bash
VECTOR_BACKEND=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=engram-index
```

##### Weaviate
```bash
VECTOR_BACKEND=weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-weaviate-key
```

### Embeddings Configuration

#### Local Embeddings (Default)
```bash
DEFAULT_EMBEDDINGS_PROVIDER=local
LOCAL_EMBEDDINGS_MODEL=all-MiniLM-L6-v2
```

#### OpenAI Embeddings
```bash
DEFAULT_EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
```

#### Google Embeddings
```bash
DEFAULT_EMBEDDINGS_PROVIDER=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_PROJECT_ID=your-project-id
```

## 📊 Monitoring and Observability

### Health Checks

1. **API Health**
   ```bash
   curl http://localhost:8000/v1/health
   ```

2. **Database Health**
   ```bash
   docker-compose exec postgres pg_isready -U engram -d engram
   ```

3. **Redis Health**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Metrics and Monitoring

#### Prometheus Metrics
```bash
# Enable Prometheus metrics
METRICS_ENABLED=true
METRICS_PORT=9090
```

#### Grafana Dashboard
```bash
# Import dashboard
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana/dashboard.json
```

### Logging

#### Structured Logging
```python
# Configure logging
import logging
from engram.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started", extra={
    "service": "engram-api",
    "version": "1.0.0"
})
```

#### Log Aggregation
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail.yml:/etc/promtail/config.yml
```

## 🔒 Security

### Authentication and Authorization

1. **JWT Configuration**
   ```bash
   JWT_SECRET_KEY=your-256-bit-secret-key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ```

2. **API Key Management**
   ```bash
   # Create API key
   docker-compose exec api python -c "
   from engram.database.apikeys import create_api_key
   key = create_api_key('admin', ['*'])
   print(f'API Key: {key}')
   "
   ```

### Data Encryption

1. **Encryption at Rest**
   ```bash
   ENCRYPTION_KEY=your-32-byte-encryption-key
   ENCRYPTION_ALGORITHM=AES-256-GCM
   ```

2. **Encryption in Transit**
   ```nginx
   # nginx.conf
   server {
       listen 443 ssl http2;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

### Network Security

1. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   ufw allow 22    # SSH
   ufw allow 80     # HTTP
   ufw allow 443    # HTTPS
   ufw allow 8000   # API (internal)
   ufw enable
   ```

2. **VPN Access**
   ```bash
   # Configure WireGuard
   wg-quick up wg0
   ```

## 🚀 Scaling

### Horizontal Scaling

1. **API Scaling**
   ```yaml
   # k8s/api-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: engram-api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: engram-api
     template:
       spec:
         containers:
         - name: api
           image: engram-api:latest
           resources:
             requests:
               memory: "512Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"
   ```

2. **Worker Scaling**
   ```yaml
   # k8s/worker-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: engram-worker
   spec:
     replicas: 2
     template:
       spec:
         containers:
         - name: worker
           image: engram-worker:latest
           resources:
             requests:
               memory: "1Gi"
               cpu: "500m"
             limits:
               memory: "2Gi"
               cpu: "1000m"
   ```

### Database Scaling

1. **Read Replicas**
   ```yaml
   # postgres-replica.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: postgres-replica
   spec:
     selector:
       app: postgres-replica
     ports:
     - port: 5432
       targetPort: 5432
   ```

2. **Connection Pooling**
   ```bash
   # PgBouncer configuration
   [databases]
   engram = host=postgres port=5432 dbname=engram
   
   [pgbouncer]
   pool_mode = transaction
   max_client_conn = 100
   default_pool_size = 20
   ```

### Caching Strategy

1. **Redis Clustering**
   ```yaml
   # redis-cluster.yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: redis-cluster
   spec:
     serviceName: redis-cluster
     replicas: 3
     template:
       spec:
         containers:
         - name: redis
           image: redis:7-alpine
           command: ["redis-server", "--cluster-enabled", "yes"]
   ```

2. **CDN Configuration**
   ```bash
   # CloudFlare configuration
   curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
     -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"CNAME","name":"api","content":"your-domain.com"}'
   ```

## 🔄 Backup and Recovery

### Database Backup

1. **Automated Backups**
   ```bash
   # backup.sh
   #!/bin/bash
   BACKUP_DIR="/backups/$(date +%Y%m%d)"
   mkdir -p $BACKUP_DIR
   
   pg_dump -h postgres -U engram engram > $BACKUP_DIR/engram.sql
   tar -czf $BACKUP_DIR/engram-$(date +%Y%m%d_%H%M%S).tar.gz $BACKUP_DIR/engram.sql
   ```

2. **S3 Backup**
   ```bash
   # s3-backup.sh
   aws s3 cp $BACKUP_DIR/engram-$(date +%Y%m%d_%H%M%S).tar.gz s3://your-backup-bucket/
   ```

### Vector Database Backup

1. **ChromaDB Backup**
   ```bash
   # chroma-backup.sh
   tar -czf chroma-backup-$(date +%Y%m%d_%H%M%S).tar.gz /data/chroma/
   ```

### Disaster Recovery

1. **Recovery Procedure**
   ```bash
   # Restore database
   psql -h postgres -U engram engram < backup/engram.sql
   
   # Restore vector database
   tar -xzf chroma-backup.tar.gz -C /data/
   
   # Restart services
   docker-compose restart
   ```

## 📈 Performance Optimization

### Database Optimization

1. **Index Optimization**
   ```sql
   -- Create indexes for better performance
   CREATE INDEX CONCURRENTLY idx_memories_tenant_user_created 
   ON memories(tenant_id, user_id, created_at);
   
   CREATE INDEX CONCURRENTLY idx_memories_text_search 
   ON memories USING gin(to_tsvector('english', text));
   ```

2. **Query Optimization**
   ```python
   # Use connection pooling
   from sqlalchemy.pool import QueuePool
   
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=20,
       max_overflow=30
   )
   ```

### API Optimization

1. **Response Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_embeddings(text: str):
       return embeddings_facade.embed_texts([text])[0]
   ```

2. **Async Processing**
   ```python
   # Use async for I/O operations
   async def process_memory_async(memory_data):
       async with aiohttp.ClientSession() as session:
           async with session.post(url, json=memory_data) as response:
               return await response.json()
   ```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/ -v --cov=engram

# Run with coverage
pytest --cov=engram --cov-report=html
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/ -v

# Test with real services
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/ -v
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## 📚 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker-compose exec api python -c "
   from engram.database.postgres import get_db_session
   with get_db_session() as db:
       print('Database connected successfully')
   "
   ```

2. **Vector Database Issues**
   ```bash
   # Check ChromaDB status
   curl http://localhost:8001/api/v1/version
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits
   docker-compose up -d --scale api=2
   ```

### Log Analysis

1. **API Logs**
   ```bash
   # View API logs
   docker-compose logs -f api
   
   # Filter error logs
   docker-compose logs api | grep ERROR
   ```

2. **Worker Logs**
   ```bash
   # View worker logs
   docker-compose logs -f worker
   ```

### Performance Debugging

1. **Database Query Analysis**
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_statement = 'all';
   ALTER SYSTEM SET log_min_duration_statement = 1000;
   SELECT pg_reload_conf();
   ```

2. **API Performance**
   ```bash
   # Use APM tools
   pip install newrelic
   newrelic-admin run-program python -m engram.api.server
   ```

## 📞 Support

### Getting Help

1. **Documentation**: Check the `/docs` endpoint for API documentation
2. **Issues**: Report issues on GitHub
3. **Community**: Join our Discord server
4. **Enterprise**: Contact support@engram.ai

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

For more detailed information, see the [Architecture Documentation](docs/architecture.md) and [API Reference](docs/api_reference.md).
