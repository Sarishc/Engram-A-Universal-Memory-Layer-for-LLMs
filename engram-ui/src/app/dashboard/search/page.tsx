"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Search, Filter, Clock, Star, ExternalLink, FileText } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { MemoryCard } from "@/components/memory-card"
import { SearchFilters } from "@/components/search-filters"
import { useQuery } from "@tanstack/react-query"
import { apiClient, Memory } from "@/lib/api"
import { debounce } from "@/lib/utils"

// Mock search results
const mockSearchResults: Memory[] = [
  {
    id: "1",
    text: "Meeting notes from Q4 planning session. Key decisions: focus on AI integration, expand to enterprise market, hire 5 new engineers. Budget allocation: $2M for R&D, $1.5M for marketing.",
    metadata: { source: "meeting-notes.pdf", importance: 0.9 },
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-15T10:30:00Z",
    tenant_id: "demo-tenant",
    user_id: "demo-user",
    modality: "pdf",
    source: "meeting-notes.pdf",
    tags: ["meeting", "planning", "Q4", "budget"],
    importance: 0.9
  },
  {
    id: "2",
    text: "Research on transformer architectures for long-context understanding. Key papers: Longformer, BigBird, and recent work on sparse attention patterns. Performance benchmarks show 40% improvement in efficiency.",
    metadata: { source: "research-notes.md", importance: 0.8 },
    created_at: "2024-01-14T15:45:00Z",
    updated_at: "2024-01-14T15:45:00Z",
    tenant_id: "demo-tenant",
    user_id: "demo-user",
    modality: "text",
    source: "research-notes.md",
    tags: ["research", "AI", "transformers", "performance"],
    importance: 0.8
  },
  {
    id: "3",
    text: "Customer feedback from beta testing. Users love the search functionality but want better mobile experience. Feature requests: dark mode, offline sync, voice search.",
    metadata: { source: "feedback-slack", importance: 0.7 },
    created_at: "2024-01-14T09:20:00Z",
    updated_at: "2024-01-14T09:20:00Z",
    tenant_id: "demo-tenant",
    user_id: "demo-user",
    modality: "chat",
    source: "feedback-slack",
    tags: ["feedback", "beta", "mobile", "features"],
    importance: 0.7
  }
]

export default function SearchPage() {
  const [query, setQuery] = useState("")
  const [filters, setFilters] = useState({
    modalities: [] as string[],
    dateRange: null as { start: string; end: string } | null,
    importanceThreshold: 0
  })
  const [showFilters, setShowFilters] = useState(false)

  // Mock search query - in real app, this would be an actual API call
  const { data: searchResults, isLoading } = useQuery({
    queryKey: ["search", query, filters],
    queryFn: async () => {
      if (!query.trim()) return { memories: [], total: 0, query_time_ms: 0 }
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Filter results based on query and filters
      let filteredResults = mockSearchResults.filter(memory => 
        memory.text.toLowerCase().includes(query.toLowerCase()) ||
        memory.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
      )

      if (filters.modalities.length > 0) {
        filteredResults = filteredResults.filter(memory => 
          filters.modalities.includes(memory.modality)
        )
      }

      if (filters.importanceThreshold > 0) {
        filteredResults = filteredResults.filter(memory => 
          memory.importance >= filters.importanceThreshold
        )
      }

      return {
        memories: filteredResults,
        total: filteredResults.length,
        query_time_ms: Math.random() * 100 + 50
      }
    },
    enabled: query.length > 0
  })

  const debouncedSearch = debounce((searchQuery: string) => {
    setQuery(searchQuery)
  }, 300)

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    debouncedSearch(e.target.value)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Search Memories
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Find anything in your knowledge base with AI-powered search.
        </p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                placeholder="Ask Engram anything... (e.g., 'Q4 planning meeting', 'AI research', 'customer feedback')"
                className="pl-10 h-12 text-lg"
                onChange={handleSearch}
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="px-4"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>

          {/* Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700"
            >
              <SearchFilters
                filters={filters}
                onFiltersChange={setFilters}
              />
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Search Results */}
      {query && (
        <div className="space-y-6">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">
                {isLoading ? "Searching..." : `Found ${searchResults?.total || 0} results`}
              </h2>
              {searchResults && (
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Search completed in {searchResults.query_time_ms.toFixed(0)}ms
                </p>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Star className="w-4 h-4 mr-2" />
                Save Search
              </Button>
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="grid gap-4">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4" />
                      <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-full" />
                      <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-2/3" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Results */}
          {!isLoading && searchResults && (
            <div className="space-y-4">
              {searchResults.memories.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <Search className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                    <h3 className="text-lg font-semibold mb-2">No results found</h3>
                    <p className="text-slate-600 dark:text-slate-400">
                      Try adjusting your search terms or filters.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                searchResults.memories.map((memory, index) => (
                  <motion.div
                    key={memory.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <MemoryCard memory={memory} />
                  </motion.div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!query && (
        <div className="text-center py-12">
          <Search className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-xl font-semibold mb-2">Start searching your memories</h3>
          <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto">
            Enter a search query above to find content in your knowledge base. 
            Try searching for topics, keywords, or even questions.
          </p>
        </div>
      )}
    </div>
  )
}
