# Engram Web UI

A modern, production-quality web interface for the Engram AI-powered second brain system.

## Features

- **Dashboard**: Overview of your knowledge base with KPIs and quick actions
- **Multimodal Ingestion**: Upload files, URLs, and chat exports
- **Advanced Search**: Filter and search through memories with multiple modalities
- **RAG Chat**: Conversational interface with automatic memory retrieval
- **Knowledge Graph**: Interactive visualization of entity relationships
- **Connectors**: Integration with Google Drive, Notion, and Slack
- **Analytics**: System performance and usage metrics
- **API Key Management**: Secure access control and scoping
- **Admin Panel**: Memory management and system administration

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: TanStack Query + Zustand
- **Charts**: Recharts
- **Graph Visualization**: Custom Canvas implementation
- **Forms**: react-hook-form + zod
- **Testing**: Playwright

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Engram API server running

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd apps/web
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp env.example .env.local
```

Edit `.env.local` with your configuration:
```env
ENGRAM_API_BASE=http://localhost:8000
ENGRAM_API_KEY=your-api-key-here
NEXT_PUBLIC_APP_NAME=Engram
NEXT_PUBLIC_APP_VERSION=1.0.0
```

4. Start the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run test` - Run Playwright tests
- `npm run test:ui` - Run tests with UI

## Docker Deployment

### Build and run with Docker:

```bash
# Build the image
docker build -t engram-web .

# Run the container
docker run -p 3000:3000 \
  -e ENGRAM_API_BASE=http://your-api-server:8000 \
  -e ENGRAM_API_KEY=your-api-key \
  engram-web
```

### Docker Compose

Add to your `docker-compose.yml`:

```yaml
services:
  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    environment:
      - ENGRAM_API_BASE=http://api:8000
      - ENGRAM_API_KEY=${ENGRAM_API_KEY}
    depends_on:
      - api
```

## Project Structure

```
apps/web/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Dashboard
│   │   ├── ingest/          # Ingestion pages
│   │   ├── search/          # Search interface
│   │   ├── chat/            # RAG chat
│   │   ├── graph/           # Knowledge graph
│   │   ├── connectors/      # External integrations
│   │   ├── analytics/       # System metrics
│   │   ├── keys/            # API key management
│   │   ├── admin/           # Admin panel
│   │   └── settings/        # User settings
│   ├── components/          # Reusable components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── nav/             # Navigation components
│   │   ├── common/          # Common utilities
│   │   ├── search/          # Search components
│   │   ├── results/         # Search results
│   │   ├── chat/            # Chat components
│   │   ├── graph/           # Graph visualization
│   │   └── forms/           # Form components
│   ├── lib/                 # Utilities and configuration
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types
│   │   ├── query.ts         # React Query setup
│   │   ├── config.ts        # Configuration
│   │   ├── format.ts        # Formatting utilities
│   │   └── utils.ts         # General utilities
│   └── store/               # Zustand stores
│       ├── ui.ts            # UI state
│       └── chat.ts          # Chat state
├── tests/                   # Playwright tests
├── public/                  # Static assets
├── Dockerfile              # Docker configuration
├── package.json            # Dependencies
└── README.md               # This file
```

## Key Features

### Dashboard
- Real-time KPIs and system status
- Quick actions for common tasks
- Recent jobs and memories preview
- System health indicators

### Multimodal Ingestion
- **URL Ingestion**: Web pages, PDFs, images, videos
- **File Upload**: Drag & drop with progress tracking
- **Chat Import**: JSON import from various platforms
- **Background Processing**: Job status tracking

### Advanced Search
- Natural language queries
- Multi-modal filtering (text, web, PDF, image, video, chat)
- Date range and importance filtering
- Real-time preview panel
- Keyboard shortcuts (⌘K)

### RAG Chat
- Conversational AI with memory context
- Automatic memory retrieval and injection
- Streaming responses
- Session management
- Context peek panel

### Knowledge Graph
- Interactive entity visualization
- Force-directed layout
- Entity search and filtering
- Node details and relationships
- Export capabilities

### Connectors
- **Google Drive**: Document sync
- **Notion**: Page and database import
- **Slack**: Message history import
- OAuth integration
- Automated sync scheduling

### Analytics
- API usage metrics
- Performance monitoring
- Content distribution analysis
- Job processing statistics
- System health dashboard

### API Key Management
- Secure key generation
- Scope-based permissions
- Usage tracking
- Key rotation and revocation

### Admin Panel
- Memory management
- Bulk operations
- System configuration
- User management
- Data export/import

## Configuration

### Environment Variables

- `ENGRAM_API_BASE`: Engram API server URL
- `ENGRAM_API_KEY`: API key for authentication
- `NEXT_PUBLIC_APP_NAME`: Application name
- `NEXT_PUBLIC_APP_VERSION`: Application version

### API Integration

The web UI integrates with the Engram API through a typed client (`src/lib/api.ts`) that handles:

- Authentication with API keys
- Request/response typing
- Error handling and retries
- Request logging and analytics

### State Management

- **TanStack Query**: Server state and caching
- **Zustand**: Client state (UI, chat sessions)
- **Local Storage**: Persistent user preferences

## Testing

### Playwright Tests

Run the test suite:

```bash
npm run test
```

Run tests with UI:

```bash
npm run test:ui
```

### Test Coverage

- Dashboard functionality
- Search and filtering
- Ingestion workflows
- Chat interactions
- Navigation and routing

## Performance

### Optimization Features

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Built-in bundle analyzer
- **Caching**: Aggressive caching with React Query
- **Lazy Loading**: Component and route lazy loading

### Monitoring

- **Real-time Metrics**: Performance and usage tracking
- **Error Tracking**: Client-side error reporting
- **Analytics**: User interaction analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
