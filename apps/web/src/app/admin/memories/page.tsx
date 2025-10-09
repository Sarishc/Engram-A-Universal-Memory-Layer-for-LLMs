'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { useUIStore } from '@/store/ui';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Filter, 
  MoreHorizontal,
  Trash2,
  Edit,
  Eye,
  EyeOff,
  Download,
  Upload,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Star
} from 'lucide-react';
import { Memory, ModalityType } from '@/lib/types';
import { formatRelativeTime, formatImportance, getImportanceColor } from '@/lib/format';
import { MODALITY_COLORS } from '@/lib/config';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export default function AdminMemoriesPage() {
  const { tenantId, userId } = useUIStore();
  const queryClient = useQueryClient();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMemories, setSelectedMemories] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(20);
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined);
  const [filterModality, setFilterModality] = useState<ModalityType | undefined>(undefined);

  const { data: memoriesData, isLoading } = useQuery({
    queryKey: queryKeys.memoriesList({
      tenant_id: tenantId,
      user_id: userId,
      limit: pageSize,
      offset: currentPage * pageSize,
      active: filterActive,
    }),
    queryFn: () => api.listMemories({
      tenant_id: tenantId,
      user_id: userId,
      limit: pageSize,
      offset: currentPage * pageSize,
      active: filterActive,
    }),
    enabled: !!tenantId,
  });

  const deleteMemoryMutation = useMutation({
    mutationFn: (memoryId: string) => api.deleteMemory(memoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.memoriesList({}) });
      toast.success('Memory deleted successfully');
    },
    onError: (error: any) => {
      toast.error(`Failed to delete memory: ${error.message}`);
    },
  });

  const handleSelectMemory = (memoryId: string) => {
    setSelectedMemories(prev => 
      prev.includes(memoryId)
        ? prev.filter(id => id !== memoryId)
        : [...prev, memoryId]
    );
  };

  const handleSelectAll = () => {
    if (memoriesData?.memories) {
      setSelectedMemories(
        selectedMemories.length === memoriesData.memories.length
          ? []
          : memoriesData.memories.map(m => m.id)
      );
    }
  };

  const handleDeleteSelected = () => {
    selectedMemories.forEach(memoryId => {
      deleteMemoryMutation.mutate(memoryId);
    });
    setSelectedMemories([]);
  };

  const filteredMemories = memoriesData?.memories.filter(memory => {
    if (searchQuery && !memory.text.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (filterModality && memory.modality !== filterModality) {
      return false;
    }
    return true;
  }) || [];

  const totalPages = memoriesData?.total_count ? Math.ceil(memoriesData.total_count / pageSize) : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Memory Management</h1>
          <p className="text-muted-foreground">
            View and manage all memories in your knowledge base
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search memories..."
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Status</label>
              <select
                value={filterActive === undefined ? '' : filterActive.toString()}
                onChange={(e) => setFilterActive(
                  e.target.value === '' ? undefined : e.target.value === 'true'
                )}
                className="w-full p-2 border rounded-lg"
              >
                <option value="">All</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Modality</label>
              <select
                value={filterModality || ''}
                onChange={(e) => setFilterModality(
                  e.target.value ? e.target.value as ModalityType : undefined
                )}
                className="w-full p-2 border rounded-lg"
              >
                <option value="">All</option>
                <option value="text">Text</option>
                <option value="web">Web</option>
                <option value="pdf">PDF</option>
                <option value="image">Image</option>
                <option value="video">Video</option>
                <option value="chat">Chat</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery('');
                  setFilterActive(undefined);
                  setFilterModality(undefined);
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedMemories.length > 0 && (
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {selectedMemories.length} memories selected
              </span>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeleteSelected}
                  disabled={deleteMemoryMutation.isPending}
                >
                  {deleteMemoryMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Trash2 className="h-4 w-4 mr-2" />
                  )}
                  Delete Selected
                </Button>
                <Button variant="outline" size="sm">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Metadata
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Memories Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              Memories ({memoriesData?.total_count || 0})
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {selectedMemories.length === filteredMemories.length ? 'Deselect All' : 'Select All'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-muted rounded-lg" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredMemories.map((memory) => (
                <div
                  key={memory.id}
                  className={`flex items-center space-x-4 p-4 border rounded-lg transition-colors ${
                    selectedMemories.includes(memory.id) ? 'bg-primary/5 border-primary' : 'hover:bg-accent/50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedMemories.includes(memory.id)}
                    onChange={() => handleSelectMemory(memory.id)}
                    className="rounded"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge
                        variant="outline"
                        className={cn(
                          'text-xs',
                          MODALITY_COLORS[memory.modality as keyof typeof MODALITY_COLORS]
                        )}
                      >
                        {memory.modality}
                      </Badge>
                      
                      <Badge variant={memory.active ? 'default' : 'secondary'} className="text-xs">
                        {memory.active ? 'Active' : 'Inactive'}
                      </Badge>
                      
                      {memory.chunk_idx !== undefined && (
                        <Badge variant="outline" className="text-xs">
                          Chunk {memory.chunk_idx + 1}
                        </Badge>
                      )}
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                      {memory.text}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <Star className={cn('h-3 w-3', getImportanceColor(memory.importance))} />
                        <span>{formatImportance(memory.importance)}</span>
                      </div>
                      
                      <span>Created {formatRelativeTime(memory.created_at)}</span>
                      
                      {memory.source_uri && (
                        <span className="truncate">Source: {memory.source_uri}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMemoryMutation.mutate(memory.id)}
                      disabled={deleteMemoryMutation.isPending}
                    >
                      {deleteMemoryMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-muted-foreground">
                Showing {currentPage * pageSize + 1} to {Math.min((currentPage + 1) * pageSize, memoriesData?.total_count || 0)} of {memoriesData?.total_count || 0} memories
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                  disabled={currentPage === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                
                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = i;
                    return (
                      <Button
                        key={page}
                        variant={currentPage === page ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setCurrentPage(page)}
                      >
                        {page + 1}
                      </Button>
                    );
                  })}
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                  disabled={currentPage === totalPages - 1}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}