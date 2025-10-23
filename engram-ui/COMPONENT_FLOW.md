# Engram Frontend — Component Interaction Flow

## 🧩 Component Hierarchy & Data Flow

```mermaid
graph TB
    %% App Root
    subgraph "🏗️ App Root (app/layout.tsx)"
        direction TB
        ROOT[📱 App Root<br/>Global Layout + Providers]
        
        subgraph "🌐 Global Providers"
            THEME[🎨 ThemeProvider<br/>Dark/Light Mode]
            QUERY[⚡ QueryClientProvider<br/>API State Management]
            ZUSTAND[🗃️ Zustand Store<br/>Global State]
        end
        
        subgraph "🧭 Navigation Components"
            NAVBAR[🧭 Navbar<br/>Top Navigation]
            SIDEBAR[📋 Sidebar<br/>Dashboard Navigation]
        end
    end
    
    %% Page Components
    subgraph "📄 Page Components"
        direction TB
        
        subgraph "🏠 Landing Page (/)"
            HERO[🎯 HeroSection<br/>Animated Intro + CTA]
            FEATURES[✨ FeatureCards<br/>4 Floating Tiles]
            HOWITWORKS[🔄 HowItWorks<br/>3-Step Process]
            FOOTER[📞 Footer<br/>Links + Social]
        end
        
        subgraph "📊 Dashboard (/dashboard)"
            STATS[📈 StatsPanel<br/>User Analytics]
            RECENT[📋 RecentMemories<br/>Latest Uploads]
            PROGRESS[⏳ ProgressBars<br/>Task Status]
        end
        
        subgraph "📤 Upload Page (/upload)"
            DROPZONE[📁 FileDropZone<br/>Drag & Drop]
            METADATA[📝 MetadataForm<br/>Tags + Categories]
            UPLOADPROG[📊 UploadProgress<br/>Animated Tracker]
        end
        
        subgraph "🔍 Search Page (/search)"
            SEARCHBAR[🔍 SearchBar<br/>Input + Auto-focus]
            RESULTS[📋 SearchResults<br/>Memory Cards]
            FILTERS[🔧 FilterPanel<br/>Tags + Date + Source]
        end
        
        subgraph "🕸️ Knowledge Graph (/graph)"
            GRAPHVIEW[🌐 GraphView<br/>3D Visualization]
            NODEDETAIL[📋 NodeDetailPanel<br/>Selected Node Info]
            LEGEND[🎨 GraphLegend<br/>Color Key]
        end
        
        subgraph "🔗 Connectors (/connectors)"
            INTCARDS[📋 IntegrationCards<br/>Drive + Notion + Slack]
            OAUTH[🔐 OAuthModal<br/>Authentication Flow]
            CONNSTATUS[📈 ConnectionStatus<br/>Sync Status]
        end
        
        subgraph "⚙️ Settings (/settings)"
            PROFILE[👤 ProfileForm<br/>User Information]
            APIKEYS[🔑 APIKeyManager<br/>Key Management]
            THEMETOGGLE[🎨 ThemeToggle<br/>Dark/Light Switch]
        end
    end
    
    %% Shared Components
    subgraph "🧩 Shared Components"
        direction TB
        MEMCARD[📋 MemoryCard<br/>Search Result Display]
        MODAL[🪟 Modal<br/>Detail Views]
        TOAST[🍞 Toast<br/>Notifications]
        LOADING[⏳ LoadingSpinner<br/>Async States]
        BUTTON[🔘 Button<br/>Shadcn/UI Component]
        INPUT[📝 Input<br/>Form Controls]
    end
    
    %% State Management
    subgraph "🔄 State Management Flow"
        direction TB
        
        subgraph "⚡ React Query (API State)"
            QUERYCACHE[🗄️ Query Cache<br/>API Response Cache]
            MUTATIONS[🔄 Mutations<br/>POST/PUT/DELETE]
            INVALIDATION[♻️ Cache Invalidation<br/>Data Refresh]
        end
        
        subgraph "🗃️ Zustand Store (Global State)"
            USERSTATE[👤 User State<br/>Authentication]
            THEMESTATE[🎨 Theme State<br/>Dark/Light Mode]
            SELECTEDNODE[🕸️ Selected Node<br/>Graph Selection]
            UPLOADID[📤 Last Upload ID<br/>Progress Tracking]
        end
        
        subgraph "🎭 React Context (Theme + User)"
            THEMECONTEXT[🎨 Theme Context<br/>Global Theme]
            USERCONTEXT[👤 User Context<br/>Session Data]
        end
    end
    
    %% API Interactions
    subgraph "🌐 API Interactions"
        direction TB
        
        subgraph "📡 Memory API Calls"
            UPLOADAPI[📤 /api/memories/upload<br/>File Processing]
            SEARCHAPI[🔍 /api/memories/search<br/>Semantic Retrieval]
            GRAPHAPI[🕸️ /api/memories/graph<br/>Relationship Data]
            STATSAPI[📊 /api/memories/stats<br/>User Analytics]
        end
        
        subgraph "🔗 Connector API Calls"
            AUTHAPI[🔐 /api/connectors/auth<br/>OAuth Flow]
            SYNCAPI[🔄 /api/connectors/sync<br/>Data Sync]
            STATUSAPI[📈 /api/connectors/status<br/>Connection Health]
        end
        
        subgraph "👤 User API Calls"
            PROFILEAPI[👤 /api/user/profile<br/>User Management]
            KEYSAPI[🔑 /api/user/keys<br/>API Key Management]
        end
    end
    
    %% User Interaction Flows
    subgraph "👆 User Interaction Flows"
        direction TB
        
        subgraph "📤 Upload Flow"
            UPLOAD1[1. User drops file]
            UPLOAD2[2. FileDropZone validates]
            UPLOAD3[3. MetadataForm collects tags]
            UPLOAD4[4. UploadProgress shows status]
            UPLOAD5[5. API call to /upload]
            UPLOAD6[6. Polling for completion]
            UPLOAD7[7. Success toast + refresh]
        end
        
        subgraph "🔍 Search Flow"
            SEARCH1[1. User types query]
            SEARCH2[2. Debounced input]
            SEARCH3[3. API call to /search]
            SEARCH4[4. Results cached in React Query]
            SEARCH5[5. Animated result cards]
            SEARCH6[6. Click opens MemoryModal]
        end
        
        subgraph "🕸️ Graph Flow"
            GRAPH1[1. Graph loads on mount]
            GRAPH2[2. API call to /graph]
            GRAPH3[3. 3D visualization renders]
            GRAPH4[4. User clicks node]
            GRAPH5[5. NodeDetailPanel opens]
            GRAPH6[6. State synced globally]
        end
        
        subgraph "🔗 Connect Flow"
            CONN1[1. User clicks "Connect"]
            CONN2[2. OAuthModal opens]
            CONN3[3. OAuth flow completes]
            CONN4[4. API call to /auth]
            CONN5[5. ConnectionStatus updates]
            CONN6[6. Sync worker starts]
        end
    end
    
    %% Data Flow Connections
    ROOT --> THEME
    ROOT --> QUERY
    ROOT --> ZUSTAND
    ROOT --> NAVBAR
    ROOT --> SIDEBAR
    
    %% Page connections
    HERO --> DASH
    DASH --> UPLOAD
    UPLOAD --> SEARCH
    SEARCH --> GRAPH
    GRAPH --> CONN
    CONN --> SETTINGS
    
    %% Component interactions
    DROPZONE --> METADATA
    METADATA --> UPLOADPROG
    SEARCHBAR --> RESULTS
    RESULTS --> MEMCARD
    GRAPHVIEW --> NODEDETAIL
    INTCARDS --> OAUTH
    
    %% State management
    QUERY --> QUERYCACHE
    QUERY --> MUTATIONS
    QUERY --> INVALIDATION
    ZUSTAND --> USERSTATE
    ZUSTAND --> THEMESTATE
    ZUSTAND --> SELECTEDNODE
    ZUSTAND --> UPLOADID
    
    %% API connections
    UPLOADPROG --> UPLOADAPI
    RESULTS --> SEARCHAPI
    GRAPHVIEW --> GRAPHAPI
    STATS --> STATSAPI
    OAUTH --> AUTHAPI
    CONNSTATUS --> SYNCAPI
    CONNSTATUS --> STATUSAPI
    PROFILE --> PROFILEAPI
    APIKEYS --> KEYSAPI
    
    %% User flows
    UPLOAD1 --> UPLOAD2 --> UPLOAD3 --> UPLOAD4 --> UPLOAD5 --> UPLOAD6 --> UPLOAD7
    SEARCH1 --> SEARCH2 --> SEARCH3 --> SEARCH4 --> SEARCH5 --> SEARCH6
    GRAPH1 --> GRAPH2 --> GRAPH3 --> GRAPH4 --> GRAPH5 --> GRAPH6
    CONN1 --> CONN2 --> CONN3 --> CONN4 --> CONN5 --> CONN6
    
    %% Styling
    classDef root fill:#3b82f6,stroke:#1e40af,stroke-width:3px,color:#fff
    classDef pages fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef components fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    classDef state fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    classDef api fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    classDef flow fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    
    class ROOT,THEME,QUERY,ZUSTAND,NAVBAR,SIDEBAR root
    class HERO,FEATURES,HOWITWORKS,FOOTER,STATS,RECENT,PROGRESS,DROPZONE,METADATA,UPLOADPROG,SEARCHBAR,RESULTS,FILTERS,GRAPHVIEW,NODEDETAIL,LEGEND,INTCARDS,OAUTH,CONNSTATUS,PROFILE,APIKEYS,THEMETOGGLE pages
    class MEMCARD,MODAL,TOAST,LOADING,BUTTON,INPUT components
    class QUERYCACHE,MUTATIONS,INVALIDATION,USERSTATE,THEMESTATE,SELECTEDNODE,UPLOADID,THEMECONTEXT,USERCONTEXT state
    class UPLOADAPI,SEARCHAPI,GRAPHAPI,STATSAPI,AUTHAPI,SYNCAPI,STATUSAPI,PROFILEAPI,KEYSAPI api
    class UPLOAD1,UPLOAD2,UPLOAD3,UPLOAD4,UPLOAD5,UPLOAD6,UPLOAD7,SEARCH1,SEARCH2,SEARCH3,SEARCH4,SEARCH5,SEARCH6,GRAPH1,GRAPH2,GRAPH3,GRAPH4,GRAPH5,GRAPH6,CONN1,CONN2,CONN3,CONN4,CONN5,CONN6 flow
```

## 🔄 Component Communication Patterns

### 1️⃣ **Parent → Child Props**
```typescript
// Dashboard passes data to child components
<StatsPanel stats={stats} loading={isLoading} />
<RecentMemories memories={memories} onRefresh={refetch} />
```

### 2️⃣ **Child → Parent Callbacks**
```typescript
// Upload component notifies parent of completion
<FileDropZone onUploadComplete={(taskId) => {
  setLastUploadId(taskId);
  invalidateQueries(['memories']);
}} />
```

### 3️⃣ **Global State (Zustand)**
```typescript
// Global state accessible from any component
const { selectedNode, setSelectedNode } = useStore();
const { theme, toggleTheme } = useThemeStore();
```

### 4️⃣ **React Query Cache**
```typescript
// Automatic cache management and synchronization
const { data: memories, refetch } = useQuery({
  queryKey: ['memories', 'search', query],
  queryFn: () => searchMemories(query),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

### 5️⃣ **Context Providers**
```typescript
// Theme and user context for global access
const { theme, setTheme } = useTheme();
const { user, setUser } = useUser();
```

## 🎯 Key Interaction Patterns

### **Upload Flow State Management**
1. **Local State**: File selection, metadata form
2. **API Call**: Upload endpoint with progress tracking
3. **Global State**: Last upload ID for cross-component updates
4. **Cache Invalidation**: Refresh dashboard and recent memories

### **Search Flow State Management**
1. **Debounced Input**: Prevents excessive API calls
2. **Query Cache**: Results cached for instant re-renders
3. **Filter State**: Local state for UI, API state for data
4. **Modal State**: Selected memory details in global state

### **Graph Flow State Management**
1. **Graph Data**: Fetched once, cached globally
2. **Selection State**: Currently selected node in Zustand
3. **View State**: Zoom, pan, and layout in local state
4. **Detail Panel**: Selected node data from global state

---

*This component flow ensures smooth user interactions with proper state management, caching, and real-time updates across the entire Engram application.*
