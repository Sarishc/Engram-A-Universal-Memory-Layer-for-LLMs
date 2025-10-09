'use client';

import { useState, useEffect } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import { Search, X, Filter, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/store/ui';
import { debounce } from '@/lib/utils';

interface SearchBarProps {
  onSearch: (query: string, filters: any) => void;
  isLoading?: boolean;
  className?: string;
  placeholder?: string;
  showFilters?: boolean;
  onToggleFilters?: () => void;
}

export function SearchBar({
  onSearch,
  isLoading = false,
  className,
  placeholder = "Search memories...",
  showFilters = true,
  onToggleFilters,
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const { searchQuery, setSearchQuery } = useUIStore();

  // Debounced search function
  const debouncedSearch = debounce((searchQuery: string) => {
    if (searchQuery.trim()) {
      onSearch(searchQuery, {});
    }
  }, 300);

  // Update query from global state
  useEffect(() => {
    if (searchQuery && searchQuery !== query) {
      setQuery(searchQuery);
      debouncedSearch(searchQuery);
    }
  }, [searchQuery]);

  // Handle query change
  const handleQueryChange = (value: string) => {
    setQuery(value);
    setSearchQuery(value);
    debouncedSearch(value);
  };

  // Handle clear
  const handleClear = () => {
    setQuery('');
    setSearchQuery('');
  };

  // Keyboard shortcuts
  useHotkeys('cmd+k, ctrl+k', (e) => {
    e.preventDefault();
    // Focus is handled by parent component
  });

  useHotkeys('escape', () => {
    if (isFocused) {
      handleClear();
    }
  });

  return (
    <div className={cn('relative', className)}>
      <div className={cn(
        'relative flex items-center transition-all duration-200',
        isFocused && 'ring-2 ring-ring ring-offset-2 rounded-lg'
      )}>
        <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
        
        <Input
          type="text"
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="pl-10 pr-20"
        />

        <div className="absolute right-2 flex items-center space-x-1">
          {isLoading && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          )}
          
          {query && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClear}
              className="h-6 w-6"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
          
          {showFilters && onToggleFilters && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleFilters}
              className="h-6 w-6"
            >
              <Filter className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>

      {/* Quick suggestions */}
      {isFocused && query.length > 2 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-popover border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
          <div className="p-2">
            <div className="text-xs text-muted-foreground mb-2">Recent searches</div>
            <div className="space-y-1">
              {['project documentation', 'meeting notes', 'code snippets'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleQueryChange(suggestion)}
                  className="w-full text-left px-2 py-1 text-sm hover:bg-accent rounded"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search tips */}
      {isFocused && query.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-popover border rounded-lg shadow-lg z-50">
          <div className="p-3">
            <div className="text-xs text-muted-foreground mb-2">Search tips</div>
            <div className="space-y-1 text-xs">
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">⌘K</Badge>
                <span>Quick search shortcut</span>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">modality:pdf</Badge>
                <span>Filter by content type</span>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">"exact phrase"</Badge>
                <span>Search for exact phrases</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
