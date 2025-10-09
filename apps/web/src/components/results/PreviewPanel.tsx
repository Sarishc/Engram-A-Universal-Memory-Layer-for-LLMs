'use client';

import { useState } from 'react';
import { Memory, ModalityType } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Globe, 
  Image, 
  Video, 
  MessageSquare,
  ExternalLink,
  Download,
  Copy,
  Star,
  Calendar,
  User,
  X,
  Eye,
  EyeOff
} from 'lucide-react';
import { cn, formatRelativeTime, formatImportance, getImportanceColor } from '@/lib/utils';
import { MODALITY_COLORS } from '@/lib/config';

interface PreviewPanelProps {
  memory: Memory | null;
  onClose: () => void;
  onSendToChat?: (memory: Memory) => void;
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

export function PreviewPanel({
  memory,
  onClose,
  onSendToChat,
  className,
}: PreviewPanelProps) {
  const [showFullText, setShowFullText] = useState(false);

  if (!memory) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center text-muted-foreground">
            <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Select a memory to preview</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const ModalityIcon = modalityIcons[memory.modality] || FileText;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(memory.text);
  };

  const downloadContent = () => {
    const blob = new Blob([memory.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `memory-${memory.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const openSource = () => {
    if (memory.source_uri) {
      window.open(memory.source_uri, '_blank');
    }
  };

  const displayText = showFullText ? memory.text : memory.text.slice(0, 1000);
  const hasMoreText = memory.text.length > 1000;

  return (
    <Card className={cn('h-full flex flex-col', className)}>
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <ModalityIcon className="h-5 w-5" />
            <span>Memory Preview</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
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
      </CardHeader>

      <CardContent className="flex-1 overflow-auto space-y-4">
        {/* Content */}
        <div className="space-y-3">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <p className="whitespace-pre-wrap leading-relaxed">
              {displayText}
            </p>
          </div>
          
          {hasMoreText && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFullText(!showFullText)}
              className="w-full"
            >
              {showFullText ? (
                <>
                  <EyeOff className="h-4 w-4 mr-2" />
                  Show Less
                </>
              ) : (
                <>
                  <Eye className="h-4 w-4 mr-2" />
                  Show Full Text
                </>
              )}
            </Button>
          )}
        </div>

        {/* Metadata */}
        <div className="space-y-3 pt-4 border-t">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Star className={cn('h-4 w-4', getImportanceColor(memory.importance))} />
                <span className="font-medium">Importance:</span>
                <span>{formatImportance(memory.importance)}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Created:</span>
                <span>{formatRelativeTime(memory.created_at)}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Updated:</span>
                <span>{formatRelativeTime(memory.updated_at)}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">Last Accessed:</span>
                <span>{formatRelativeTime(memory.last_accessed_at)}</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="font-medium">ID:</span>
                <code className="text-xs bg-muted px-1 rounded">{memory.id}</code>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="font-medium">User:</span>
                <span className="text-xs bg-muted px-1 rounded">{memory.user_id}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="font-medium">Tenant:</span>
                <span className="text-xs bg-muted px-1 rounded">{memory.tenant_id}</span>
              </div>
              
              {memory.mime && (
                <div className="flex items-center space-x-2">
                  <span className="font-medium">MIME:</span>
                  <span className="text-xs bg-muted px-1 rounded">{memory.mime}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Source */}
        {memory.source_uri && (
          <div className="space-y-2 pt-4 border-t">
            <h4 className="font-medium">Source</h4>
            <div className="flex items-center space-x-2">
              <code className="flex-1 text-xs bg-muted p-2 rounded truncate">
                {memory.source_uri}
              </code>
              <Button variant="outline" size="sm" onClick={openSource}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Caption/Transcript */}
        {memory.caption_or_transcript && (
          <div className="space-y-2 pt-4 border-t">
            <h4 className="font-medium">Caption/Transcript</h4>
            <p className="text-sm bg-muted p-3 rounded">
              {memory.caption_or_transcript}
            </p>
          </div>
        )}

        {/* Metadata */}
        {Object.keys(memory.metadata).length > 0 && (
          <div className="space-y-2 pt-4 border-t">
            <h4 className="font-medium">Metadata</h4>
            <div className="bg-muted p-3 rounded">
              <pre className="text-xs overflow-auto">
                {JSON.stringify(memory.metadata, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </CardContent>

      {/* Actions */}
      <div className="flex-shrink-0 p-4 border-t">
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={copyToClipboard}
            className="flex-1"
          >
            <Copy className="h-4 w-4 mr-2" />
            Copy Text
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={downloadContent}
            className="flex-1"
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          
          {onSendToChat && (
            <Button
              size="sm"
              onClick={() => onSendToChat(memory)}
              className="flex-1"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Send to Chat
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
