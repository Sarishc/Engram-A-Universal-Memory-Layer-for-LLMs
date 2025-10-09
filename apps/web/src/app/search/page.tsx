'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { useUIStore } from '@/store/ui';
import { SearchBar } from '@/components/search/SearchBar';
import { Filters } from '@/components/search/Filters';
import { MemoryCard } from '@/components/results/MemoryCard';
import { PreviewPanel } from '@/components/results/PreviewPanel';
import { EmptyState } from '@/components/common/EmptyState';
import { SkeletonCard } from '@/components/common/Skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Filter, 
  Grid, 
  List,
  Loader2,
  MessageSquare,
  Brain,
  AlertCircle
} from 'lucide-react';
import { Memory, ModalityType, SearchFilters } from '@/lib/types';
import { toast } from 'sonner';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const { tenantId, userId } = useUIStore();
  
  const [query, setQuery] = useState('');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState<SearchFilters>({
    modalities: [],
    tags: [],
    sources: [],
    authors: [],
  });

  // Get initial query from URL
  useEffect(() => {
    const urlQuery = searchParams.get('q');
    if (urlQuery) {
      setQuery(urlQuery);
    }
  }, [searchParams]);

  // Search query
  const { data: searchResults, isLoading, error } = useQuery({
    queryKey: queryKeys.memories({
      query,
      filters,
      tenant_id: tenantId,
      user_id: userId,
    }),
    queryFn: () => api.retrieve({
      query,
      top_k: 50,
      modalities: filters.modalities.length > 0 ? filters.modalities : undefined,
      filters: {
        modalities: filters.modalities.length > 0 ? filters.modalities : undefined,
        tags: filters.tags.length > 0 ? filters.tags : undefined,
        importance_min: filters.importanceMin,
        date_range: filters.dateRange ? {
          start: filters.dateRange.start.toISOString(),
          end: filters.dateRange.end.toISOString(),
        } : undefined,
      },
    }),
    enabled: !!query.trim() && !!tenantId,
  });

  const handleSearch = (searchQuery: string, searchFilters: any) => {
    setQuery(searchQuery);
    setFilters(searchFilters);
  };

  const handleMemorySelect = (memory: Memory) => {
    setSelectedMemory(memory);
  };

  const handleSendToChat = (memory: Memory) => {
    // This would integrate with the chat system
    toast.success(`Memory "${memory.id}" sent to chat`);
  };

  const clearSelection = () => {
    setSelectedMemory(null);
  };

  const hasResults = searchResults && searchResults.memories.length > 0;
  const hasFilters = 
    filters.modalities.length > 0 ||
    filters.tags.length > 0 ||
    filters.sources.length > 0 ||
    filters.authors.length > 0 ||
    filters.importanceMin !== undefined ||
    filters.dateRange !== undefined;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Search Memories</h1>
          <p className="text-muted-foreground">
            Find and explore your knowledge base
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid className="h-4 w-4" />}
          </Button>
          
          <Filters
            filters={filters}
            onFiltersChange={setFilters}
            isOpen={showFilters}
            onToggle={() => setShowFilters(!showFilters)}
          />
        </div>
      </div>

      {/* Search Bar */}
      <SearchBar
        onSearch={handleSearch}
        isLoading={isLoading}
        onToggleFilters={() => setShowFilters(!showFilters)}
      />

      {/* Active Filters */}
      {hasFilters && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Active Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {filters.modalities.map((modality) => (
                <Badge key={modality} variant="secondary">
                  {modality}
                </Badge>
              ))}
              {filters.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
              {filters.sources.map((source) => (
                <Badge key={source} variant="secondary">
                  {source}
                </Badge>
              ))}
              {filters.authors.map((author) => (
                <Badge key={author} variant="secondary">
                  {author}
                </Badge>
              ))}
              {filters.importanceMin !== undefined && (
                <Badge variant="secondary">
                  Min importance: {(filters.importanceMin * 100).toFixed(0)}%
                </Badge>
              )}
              {filters.dateRange && (
                <Badge variant="secondary">
                  {filters.dateRange.start.toLocaleDateString()} - {filters.dateRange.end.toLocaleDateString()}
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Results */}
        <div className="lg:col-span-2">
          {isLoading && (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          )}

          {error && (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4" />
                  <p>Failed to search memories</p>
                  <p className="text-sm">Please try again</p>
                </div>
              </CardContent>
            </Card>
          )}

          {!isLoading && !error && !hasResults && query && (
            <EmptyState
              icon={<Search className="h-12 w-12" />}
              title="No memories found"
              description="Try adjusting your search terms or filters"
              action={{
                label: 'Clear Filters',
                onClick: () => setFilters({
                  modalities: [],
                  tags: [],
                  sources: [],
                  authors: [],
                }),
              }}
            />
          )}

          {!isLoading && !error && !query && (
            <EmptyState
              icon={<Brain className="h-12 w-12" />}
              title="Start searching"
              description="Enter a query to search through your memories"
            />
          )}

          {hasResults && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Found {searchResults.total_count} memories
                </p>
                <div className="flex items-center space-x-2">
                  {onSendToChat && selectedMemory && (
                    <Button
                      size="sm"
                      onClick={() => handleSendToChat(selectedMemory)}
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Send to Chat
                    </Button>
                  )}
                </div>
              </div>

              <div className={
                viewMode === 'grid' 
                  ? 'grid gap-4 md:grid-cols-2' 
                  : 'space-y-4'
              }>
                {searchResults.memories.map((memory) => (
                  <MemoryCard
                    key={memory.id}
                    memory={memory}
                    onSelect={handleMemorySelect}
                    onSendToChat={handleSendToChat}
                    isSelected={selectedMemory?.id === memory.id}
                    showScore={true}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-1">
          <PreviewPanel
            memory={selectedMemory}
            onClose={clearSelection}
            onSendToChat={handleSendToChat}
            className="h-[600px]"
          />
        </div>
      </div>

      {/* Search Tips */}
      {!query && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Search Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="font-medium">Query Types</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Natural language queries</li>
                  <li>• Exact phrases with quotes</li>
                  <li>• Boolean operators (AND, OR, NOT)</li>
                  <li>• Wildcards (* and ?)</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium">Filters</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Filter by content type</li>
                  <li>• Date range filtering</li>
                  <li>• Importance threshold</li>
                  <li>• Source and author tags</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
