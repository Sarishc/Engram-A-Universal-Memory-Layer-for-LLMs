# Engram Web UI - Quick Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Docker & Docker Compose (optional)
- Engram API server running

### Option 1: Local Development

1. **Setup the web UI:**
   ```bash
   ./scripts/setup-web.sh
   ```

2. **Configure environment:**
   ```bash
   cd apps/web
   cp .env.local.example .env.local
   # Edit .env.local with your API settings
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:3000
   ```

### Option 2: Docker Compose

1. **Set environment variables:**
   ```bash
   export ENGRAM_API_KEY=your-api-key-here
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access services:**
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - RQ Dashboard: http://localhost:9181

## 🎯 Key Features

### ✅ Implemented
- **Dashboard**: KPIs, quick actions, recent activity
- **Multimodal Ingestion**: URL, file upload, chat import
- **Advanced Search**: Filters, preview panel, keyboard shortcuts
- **RAG Chat**: Streaming responses, memory context
- **Knowledge Graph**: Interactive visualization
- **Connectors**: Google Drive, Notion, Slack integration
- **Analytics**: Performance metrics, usage charts
- **API Keys**: Management with scopes
- **Admin Panel**: Memory management, bulk operations
- **Settings**: Theme, user context, API configuration

### 🎨 UI/UX Features
- **Dark-first theme** with glass morphism
- **Responsive design** for all screen sizes
- **Keyboard shortcuts** (⌘K for search, ⌘I for ingest)
- **Loading states** and skeleton screens
- **Error handling** with retry mechanisms
- **Accessibility** with proper ARIA labels
- **Smooth animations** and micro-interactions

## 📁 Project Structure

```
apps/web/
├── src/
│   ├── app/                    # Next.js pages
│   │   ├── page.tsx           # Dashboard
│   │   ├── ingest/            # Ingestion interface
│   │   ├── search/            # Search & filters
│   │   ├── chat/              # RAG chat
│   │   ├── graph/             # Knowledge graph
│   │   ├── connectors/        # External integrations
│   │   ├── analytics/         # System metrics
│   │   ├── keys/              # API key management
│   │   ├── admin/             # Admin panel
│   │   └── settings/          # User settings
│   ├── components/            # Reusable components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── nav/               # Navigation
│   │   ├── common/            # Common utilities
│   │   ├── search/            # Search components
│   │   ├── results/           # Results display
│   │   ├── chat/              # Chat components
│   │   ├── graph/             # Graph visualization
│   │   └── forms/             # Form components
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   ├── types.ts           # TypeScript types
│   │   ├── query.ts           # React Query setup
│   │   ├── config.ts          # Configuration
│   │   └── format.ts          # Formatting utilities
│   └── store/                 # State management
│       ├── ui.ts              # UI state
│       └── chat.ts            # Chat state
├── tests/                     # Playwright tests
├── Dockerfile                 # Docker configuration
└── package.json              # Dependencies
```

## 🔧 Development Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run format           # Format with Prettier

# Testing
npm run test             # Run Playwright tests
npm run test:ui          # Run tests with UI

# Docker
docker build -t engram-web .  # Build image
docker run -p 3000:3000 engram-web  # Run container
```

## 🌐 API Integration

The web UI integrates with the Engram API through a typed client that handles:

- **Authentication**: API key validation
- **Request/Response**: Full TypeScript typing
- **Error Handling**: Retry logic with exponential backoff
- **Analytics**: Request logging and metrics
- **Caching**: Smart caching with React Query

## 🎨 Design System

### Colors
- **Primary**: Indigo/blue gradient
- **Background**: Dark theme with subtle gradients
- **Cards**: Glass morphism with rounded corners
- **Accents**: Subtle shadows and highlights

### Typography
- **Headings**: Bold, gradient text
- **Body**: Clean, readable fonts
- **Code**: Monospace for technical content

### Components
- **Buttons**: Multiple variants with hover states
- **Forms**: Validation with inline feedback
- **Cards**: Consistent spacing and shadows
- **Badges**: Color-coded for different states

## 🧪 Testing

### Playwright Tests
- **Dashboard**: Loads and displays correctly
- **Search**: Performs queries and shows results
- **Ingest**: Form validation and submission
- **Chat**: Message sending and responses

### Test Coverage
- ✅ Page rendering
- ✅ Navigation
- ✅ Form interactions
- ✅ API integration
- ✅ Error handling

## 🚀 Deployment

### Production Build
```bash
npm run build
npm run start
```

### Docker Deployment
```bash
docker-compose up --build
```

### Environment Variables
```env
ENGRAM_API_BASE=http://your-api-server:8000
ENGRAM_API_KEY=your-api-key
NEXT_PUBLIC_APP_NAME=Engram
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 📊 Performance

### Optimizations
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Caching**: Aggressive caching with React Query
- **Lazy Loading**: Component and route lazy loading
- **Bundle Analysis**: Built-in bundle analyzer

### Monitoring
- **Real-time Metrics**: Performance tracking
- **Error Tracking**: Client-side error reporting
- **Analytics**: User interaction analytics

## 🔒 Security

### Authentication
- **API Keys**: Secure key management with scopes
- **Request Validation**: Client-side validation
- **Error Handling**: No sensitive data exposure

### Best Practices
- **Environment Variables**: Secure configuration
- **HTTPS**: Production SSL/TLS
- **CORS**: Proper cross-origin handling
- **Rate Limiting**: Client-side throttling

## 🆘 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check `ENGRAM_API_BASE` in `.env.local`
   - Verify API server is running
   - Test API key validity

2. **Build Errors**
   - Run `npm install` to update dependencies
   - Check TypeScript errors with `npm run lint`
   - Clear `.next` cache if needed

3. **Tests Failing**
   - Ensure API server is running
   - Check environment variables
   - Verify test data exists

### Support
- Check `apps/web/README.md` for detailed documentation
- Review console logs for error details
- Test API endpoints directly with curl/Postman

## 🎉 Success!

Your Engram Web UI is now ready! The interface provides a complete, production-quality experience for interacting with your AI-powered second brain system.

**Key URLs:**
- Dashboard: http://localhost:3000
- Search: http://localhost:3000/search
- Chat: http://localhost:3000/chat
- Graph: http://localhost:3000/graph
- Admin: http://localhost:3000/admin/memories
