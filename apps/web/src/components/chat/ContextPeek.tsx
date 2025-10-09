'use client';

import { useState } from 'react';
import { Memory } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronDown, 
  ChevronUp, 
  Eye, 
  EyeOff,
  FileText,
  Globe,
  Image,
  Video,
  MessageSquare,
  ExternalLink,
  Copy
} from 'lucide-react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { MODALITY_COLORS } from '@/lib/config';

interface ContextPeekProps {
  memories: Memory[];
  className?: string;
}

const modalityIcons = {
  text: FileText,
  web: Globe,
  pdf: FileText,
  image: Image,
  video: Video,
  chat: MessageSquare,
};

export function ContextPeek({ memories, className }: ContextPeekProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFullContext, setShowFullContext] = useState(false);

  if (memories.length === 0) {
    return null;
  }

  const visibleMemories = showFullContext ? memories : memories.slice(0, 3);
  const hasMoreMemories = memories.length > 3;

  const copyContextToClipboard = () => {
    const contextText = memories
      .map((memory, index) => `Memory ${index + 1} (${memory.modality}):\n${memory.text}`)
      .join('\n\n');
    
    navigator.clipboard.writeText(contextText);
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader 
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2 text-sm">
            <Eye className="h-4 w-4" />
            <span>Memory Context</span>
            <Badge variant="secondary" className="text-xs">
              {memories.length} memories
            </Badge>
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                copyContextToClipboard();
              }}
              className="h-6 w-6 p-0"
            >
              <Copy className="h-3 w-3" />
            </Button>
            
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          <div className="space-y-3">
            {visibleMemories.map((memory, index) => {
              const ModalityIcon = modalityIcons[memory.modality] || FileText;
              
              return (
                <div
                  key={memory.id}
                  className="p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <ModalityIcon className="h-4 w-4 text-muted-foreground" />
                      <Badge
                        variant="outline"
                        className={cn(
                          'text-xs',
                          MODALITY_COLORS[memory.modality as keyof typeof MODALITY_COLORS]
                        )}
                      >
                        {memory.modality}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {(memory as any).score ? ((memory as any).score * 100).toFixed(1) + '%' : 'N/A'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(memory.text);
                        }}
                        className="h-6 w-6 p-0"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      
                      {memory.source_uri && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(memory.source_uri, '_blank')}
                          className="h-6 w-6 p-0"
                        >
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-2">
                    {memory.text.slice(0, 150)}
                    {memory.text.length > 150 && '...'}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{formatRelativeTime(memory.created_at)}</span>
                    {memory.chunk_idx !== undefined && (
                      <Badge variant="outline" className="text-xs">
                        Chunk {memory.chunk_idx + 1}
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })}
            
            {hasMoreMemories && !showFullContext && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFullContext(true)}
                className="w-full"
              >
                <Eye className="h-4 w-4 mr-2" />
                Show {memories.length - 3} more memories
              </Button>
            )}
            
            {showFullContext && hasMoreMemories && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFullContext(false)}
                className="w-full"
              >
                <EyeOff className="h-4 w-4 mr-2" />
                Show fewer memories
              </Button>
            )}
          </div>
          
          {/* Context Summary */}
          <div className="mt-4 pt-4 border-t">
            <div className="text-xs text-muted-foreground space-y-1">
              <p><strong>Context Summary:</strong></p>
              <p>These memories will be used to provide context for the AI response.</p>
              <p>The AI will reference and build upon this information when answering your questions.</p>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
