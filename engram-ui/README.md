# Engram UI - Modern Memory Management Interface

A beautiful, modern web interface for the Engram AI-powered memory system. Built with Next.js 14, TypeScript, TailwindCSS, and Framer Motion.

## 🚀 Features

- **Modern Design**: Clean, professional interface inspired by Supermemory.ai
- **Interactive Dashboard**: Real-time stats, memory cards, and processing queue
- **Smart Search**: AI-powered semantic search with advanced filters
- **3D Knowledge Graph**: Interactive visualization of memory connections
- **File Upload**: Drag-and-drop interface for multiple file types
- **Connector Integration**: Connect with Google Drive, Notion, Slack, and more
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Mode**: Beautiful dark theme with smooth transitions
- **Animations**: Smooth Framer Motion animations throughout

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **UI Components**: Radix UI + shadcn/ui
- **Data Fetching**: TanStack Query (React Query)
- **Icons**: Lucide React
- **Graph Visualization**: D3.js
- **Notifications**: Sonner

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd engram-ui
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Update `.env.local` with your API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/            # Reusable components
│   ├── ui/               # Base UI components (shadcn/ui)
│   ├── navbar.tsx        # Navigation component
│   ├── sidebar.tsx       # Dashboard sidebar
│   ├── memory-card.tsx   # Memory display component
│   ├── graph-view.tsx    # 3D graph visualization
│   └── ...
├── lib/                  # Utilities and configurations
│   ├── api.ts           # API client
│   └── utils.ts        # Helper functions
└── styles/              # Global styles
```

## 🎨 Design System

### Colors
- **Primary**: Indigo (#4F46E5)
- **Secondary**: Purple (#7C3AED)
- **Accent**: Cyan (#06B6D4)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)

### Typography
- **Primary Font**: Inter
- **Display Font**: Poppins
- **Monospace**: JetBrains Mono

### Components
All components follow the shadcn/ui design system with custom enhancements:
- Consistent spacing and sizing
- Smooth animations and transitions
- Accessible keyboard navigation
- Responsive design patterns

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Next.js recommended configuration
- **Prettier**: Code formatting
- **Husky**: Git hooks for quality assurance

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect your repository to Vercel**
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your Engram API URL
   - `NEXT_PUBLIC_APP_URL`: Your app URL
3. **Deploy**: Automatic deployments on push to main

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- Railway
- DigitalOcean App Platform

## 🔌 API Integration

The UI connects to the Engram FastAPI backend through the following endpoints:

- `GET /v1/health` - Health check
- `POST /v1/memories/search` - Search memories
- `GET /v1/memories` - List memories
- `POST /v1/ingest/file` - Upload files
- `POST /v1/ingest/url` - Upload URLs
- `POST /v1/ingest/chat` - Upload text
- `GET /v1/graph/subgraph` - Get graph data
- `POST /v1/chat` - Chat with memories

## 🎯 Key Features

### Dashboard
- Real-time statistics and metrics
- Recent memories with previews
- Processing queue with progress bars
- Quick action buttons

### Search
- Semantic search with AI-powered results
- Advanced filtering by type, date, importance
- Real-time search suggestions
- Export and save search functionality

### Graph View
- Interactive 3D force-directed graph
- Zoom, pan, and rotate controls
- Node clustering by category
- Click to view memory details

### Upload
- Drag-and-drop file upload
- URL and text input
- Progress tracking
- Batch processing

### Connectors
- One-click integration setup
- Sync status monitoring
- Configuration management
- Error handling and retry logic

## 🎨 Customization

### Themes
The app supports light and dark themes with system preference detection. Customize colors in `tailwind.config.js`.

### Animations
All animations use Framer Motion. Customize timing and easing in component files.

### Components
Extend the design system by creating new components in `src/components/ui/`.

## 📱 Mobile Support

The interface is fully responsive with:
- Touch-friendly interactions
- Optimized layouts for mobile
- Swipe gestures for navigation
- Mobile-specific UI patterns

## 🔒 Security

- API key management
- Secure authentication flows
- Input validation and sanitization
- HTTPS enforcement in production

## 📊 Performance

- Optimized bundle size
- Lazy loading for heavy components
- Image optimization
- Caching strategies
- Lighthouse score > 90

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

---

Built with ❤️ by the Engram team