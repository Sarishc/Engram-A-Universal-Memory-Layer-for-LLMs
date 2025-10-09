'use client';

import { useState } from 'react';
import { Memory, ModalityType } from '@/lib/types';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Globe, 
  Image, 
  Video, 
  MessageSquare, 
  Star,
  Calendar,
  User,
  ExternalLink,
  Eye,
  Send,
  Copy,
  MoreHorizontal
} from 'lucide-react';
import { cn, formatRelativeTime, formatImportance, getImportanceColor } from '@/lib/utils';
import { MODALITY_COLORS } from '@/lib/config';

interface MemoryCardProps {
  memory: Memory;
  onSelect?: (memory: Memory) => void;
  onSendToChat?: (memory: Memory) => void;
  isSelected?: boolean;
  showScore?: boolean;
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

export function MemoryCard({
  memory,
  onSelect,
  onSendToChat,
  isSelected = false,
  showScore = false,
  className,
}: MemoryCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const ModalityIcon = modalityIcons[memory.modality] || FileText;

  const handleSelect = () => {
    onSelect?.(memory);
  };

  const handleSendToChat = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSendToChat?.(memory);
  };

  const copyToClipboard = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(memory.text);
  };

  const openSource = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (memory.source_uri) {
      window.open(memory.source_uri, '_blank');
    }
  };

  const truncatedText = memory.text.length > 200 && !isExpanded 
    ? memory.text.slice(0, 200) + '...' 
    : memory.text;

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-md',
        isSelected && 'ring-2 ring-primary bg-primary/5',
        className
      )}
      onClick={handleSelect}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2 flex-1 min-w-0">
            <ModalityIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <Badge
              variant="outline"
              className={cn(
                'text-xs',
                MODALITY_COLORS[memory.modality as keyof typeof MODALITY_COLORS]
              )}
            >
              {memory.modality}
            </Badge>
            {showScore && (
              <Badge variant="secondary" className="text-xs">
                {(memory as any).score ? ((memory as any).score * 100).toFixed(1) + '%' : 'N/A'}
              </Badge>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            {onSendToChat && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSendToChat}
                className="h-8 w-8"
              >
                <Send className="h-3 w-3" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={copyToClipboard}
              className="h-8 w-8"
            >
              <Copy className="h-3 w-3" />
            </Button>
            {memory.source_uri && (
              <Button
                variant="ghost"
                size="icon"
                onClick={openSource}
                className="h-8 w-8"
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
            >
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Content */}
        <div className="space-y-3">
          <p className="text-sm leading-relaxed">
            {truncatedText}
          </p>
          
          {memory.text.length > 200 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="h-8 px-2 text-xs"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </Button>
          )}
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t">
          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Star className={cn('h-3 w-3', getImportanceColor(memory.importance))} />
              <span>{formatImportance(memory.importance)}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>{formatRelativeTime(memory.created_at)}</span>
            </div>
            
            {memory.chunk_idx !== undefined && (
              <Badge variant="outline" className="text-xs">
                Chunk {memory.chunk_idx + 1}
              </Badge>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {memory.caption_or_transcript && (
              <Badge variant="outline" className="text-xs">
                <Eye className="h-3 w-3 mr-1" />
                Has transcript
              </Badge>
            )}
            
            <Badge 
              variant={memory.active ? 'default' : 'secondary'} 
              className="text-xs"
            >
              {memory.active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </div>

        {/* Source URI */}
        {memory.source_uri && (
          <div className="mt-2 pt-2 border-t">
            <p className="text-xs text-muted-foreground truncate">
              Source: {memory.source_uri}
            </p>
          </div>
        )}

        {/* Caption/Transcript */}
        {memory.caption_or_transcript && (
          <div className="mt-2 pt-2 border-t">
            <p className="text-xs text-muted-foreground">
              <strong>Caption:</strong> {memory.caption_or_transcript}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
