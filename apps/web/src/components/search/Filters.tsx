'use client';

import { useState } from 'react';
import { Calendar, Tag, User, Star, Filter, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { ModalityType } from '@/lib/types';
import { MODALITY_TYPES } from '@/lib/constants';

interface SearchFilters {
  modalities: ModalityType[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  importanceMin?: number;
  tags: string[];
  sources: string[];
  authors: string[];
}

interface FiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export function Filters({
  filters,
  onFiltersChange,
  isOpen,
  onToggle,
  className,
}: FiltersProps) {
  const [newTag, setNewTag] = useState('');
  const [newSource, setNewSource] = useState('');
  const [newAuthor, setNewAuthor] = useState('');

  const updateFilters = (updates: Partial<SearchFilters>) => {
    onFiltersChange({ ...filters, ...updates });
  };

  const toggleModality = (modality: ModalityType) => {
    const modalities = filters.modalities.includes(modality)
      ? filters.modalities.filter(m => m !== modality)
      : [...filters.modalities, modality];
    updateFilters({ modalities });
  };

  const addTag = () => {
    if (newTag.trim() && !filters.tags.includes(newTag.trim())) {
      updateFilters({ tags: [...filters.tags, newTag.trim()] });
      setNewTag('');
    }
  };

  const removeTag = (tag: string) => {
    updateFilters({ tags: filters.tags.filter(t => t !== tag) });
  };

  const addSource = () => {
    if (newSource.trim() && !filters.sources.includes(newSource.trim())) {
      updateFilters({ sources: [...filters.sources, newSource.trim()] });
      setNewSource('');
    }
  };

  const removeSource = (source: string) => {
    updateFilters({ sources: filters.sources.filter(s => s !== source) });
  };

  const addAuthor = () => {
    if (newAuthor.trim() && !filters.authors.includes(newAuthor.trim())) {
      updateFilters({ authors: [...filters.authors, newAuthor.trim()] });
      setNewAuthor('');
    }
  };

  const removeAuthor = (author: string) => {
    updateFilters({ authors: filters.authors.filter(a => a !== author) });
  };

  const clearAllFilters = () => {
    onFiltersChange({
      modalities: [],
      tags: [],
      sources: [],
      authors: [],
    });
  };

  const hasActiveFilters = 
    filters.modalities.length > 0 ||
    filters.tags.length > 0 ||
    filters.sources.length > 0 ||
    filters.authors.length > 0 ||
    filters.importanceMin !== undefined ||
    filters.dateRange !== undefined;

  if (!isOpen) {
    return (
      <Button
        variant="outline"
        onClick={onToggle}
        className={cn('relative', className)}
      >
        <Filter className="h-4 w-4 mr-2" />
        Filters
        {hasActiveFilters && (
          <Badge variant="secondary" className="ml-2 h-5 w-5 rounded-full p-0 text-xs">
            {filters.modalities.length + filters.tags.length + filters.sources.length + filters.authors.length}
          </Badge>
        )}
      </Button>
    );
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Filter className="h-5 w-5" />
            <span>Filters</span>
            {hasActiveFilters && (
              <Badge variant="secondary">
                {filters.modalities.length + filters.tags.length + filters.sources.length + filters.authors.length} active
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center space-x-2">
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                Clear all
              </Button>
            )}
            <Button variant="ghost" size="icon" onClick={onToggle}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Content Types */}
        <div className="space-y-3">
          <h4 className="font-medium">Content Types</h4>
          <div className="flex flex-wrap gap-2">
            {MODALITY_TYPES.map((type) => (
              <Badge
                key={type.value}
                variant={filters.modalities.includes(type.value as ModalityType) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleModality(type.value as ModalityType)}
              >
                {type.icon} {type.label}
              </Badge>
            ))}
          </div>
        </div>

        {/* Importance Filter */}
        <div className="space-y-3">
          <h4 className="font-medium">Minimum Importance</h4>
          <div className="space-y-2">
            <Input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={filters.importanceMin || 0}
              onChange={(e) => updateFilters({ importanceMin: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Low (0)</span>
              <span className="font-medium">
                {filters.importanceMin ? (filters.importanceMin * 100).toFixed(0) : '0'}%
              </span>
              <span>High (1)</span>
            </div>
          </div>
        </div>

        {/* Tags */}
        <div className="space-y-3">
          <h4 className="font-medium">Tags</h4>
          <div className="flex space-x-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add tag..."
              onKeyDown={(e) => e.key === 'Enter' && addTag()}
            />
            <Button onClick={addTag} disabled={!newTag.trim()}>
              Add
            </Button>
          </div>
          {filters.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {filters.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeTag(tag)}
                >
                  <Tag className="h-3 w-3 mr-1" />
                  {tag}
                  <X className="h-3 w-3 ml-1" />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Sources */}
        <div className="space-y-3">
          <h4 className="font-medium">Sources</h4>
          <div className="flex space-x-2">
            <Input
              value={newSource}
              onChange={(e) => setNewSource(e.target.value)}
              placeholder="Add source..."
              onKeyDown={(e) => e.key === 'Enter' && addSource()}
            />
            <Button onClick={addSource} disabled={!newSource.trim()}>
              Add
            </Button>
          </div>
          {filters.sources.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {filters.sources.map((source) => (
                <Badge
                  key={source}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeSource(source)}
                >
                  {source}
                  <X className="h-3 w-3 ml-1" />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Authors */}
        <div className="space-y-3">
          <h4 className="font-medium">Authors</h4>
          <div className="flex space-x-2">
            <Input
              value={newAuthor}
              onChange={(e) => setNewAuthor(e.target.value)}
              placeholder="Add author..."
              onKeyDown={(e) => e.key === 'Enter' && addAuthor()}
            />
            <Button onClick={addAuthor} disabled={!newAuthor.trim()}>
              Add
            </Button>
          </div>
          {filters.authors.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {filters.authors.map((author) => (
                <Badge
                  key={author}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeAuthor(author)}
                >
                  <User className="h-3 w-3 mr-1" />
                  {author}
                  <X className="h-3 w-3 ml-1" />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Date Range */}
        <div className="space-y-3">
          <h4 className="font-medium">Date Range</h4>
          <div className="grid gap-2 md:grid-cols-2">
            <Input
              type="date"
              value={filters.dateRange?.start?.toISOString().split('T')[0] || ''}
              onChange={(e) => {
                const start = e.target.value ? new Date(e.target.value) : undefined;
                updateFilters({
                  dateRange: start ? {
                    start,
                    end: filters.dateRange?.end || new Date(),
                  } : undefined,
                });
              }}
              placeholder="Start date"
            />
            <Input
              type="date"
              value={filters.dateRange?.end?.toISOString().split('T')[0] || ''}
              onChange={(e) => {
                const end = e.target.value ? new Date(e.target.value) : undefined;
                updateFilters({
                  dateRange: end ? {
                    start: filters.dateRange?.start || new Date(0),
                    end,
                  } : undefined,
                });
              }}
              placeholder="End date"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
