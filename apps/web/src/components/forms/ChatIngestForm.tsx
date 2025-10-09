'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useUIStore } from '@/store/ui';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Upload, 
  Loader2,
  CheckCircle,
  AlertCircle,
  FileText,
  Trash2
} from 'lucide-react';
import { toast } from 'sonner';

const chatIngestSchema = z.object({
  platform: z.string().min(1, 'Platform is required'),
  items: z.array(z.object({
    author: z.string().optional(),
    text: z.string().min(1, 'Message text is required'),
    timestamp: z.string().min(1, 'Timestamp is required'),
    metadata: z.record(z.any()).optional(),
  })).min(1, 'At least one message is required'),
  metadata: z.record(z.any()).optional(),
});

type ChatIngestFormData = z.infer<typeof chatIngestSchema>;

interface ChatMessage {
  author?: string;
  text: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

const platformOptions = [
  { value: 'slack', label: 'Slack', description: 'Slack workspace export' },
  { value: 'discord', label: 'Discord', description: 'Discord server export' },
  { value: 'teams', label: 'Microsoft Teams', description: 'Teams conversation export' },
  { value: 'whatsapp', label: 'WhatsApp', description: 'WhatsApp chat export' },
  { value: 'telegram', label: 'Telegram', description: 'Telegram chat export' },
  { value: 'generic', label: 'Generic', description: 'Generic chat format' },
] as const;

export function ChatIngestForm() {
  const router = useRouter();
  const { tenantId, userId } = useUIStore();
  const [jobId, setJobId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [jsonInput, setJsonInput] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ChatIngestFormData>({
    resolver: zodResolver(chatIngestSchema),
    defaultValues: {
      platform: 'generic',
      items: [],
      metadata: {},
    },
  });

  const selectedPlatform = watch('platform');

  const ingestMutation = useMutation({
    mutationFn: (data: ChatIngestFormData) => {
      return api.ingestChat(data);
    },
    onSuccess: (response) => {
      setJobId(response.job_id);
      toast.success('Chat ingestion job started successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to start chat ingestion job');
    },
  });

  const addMessage = () => {
    const newMessage: ChatMessage = {
      author: '',
      text: '',
      timestamp: new Date().toISOString(),
      metadata: {},
    };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    setValue('items', updatedMessages);
  };

  const updateMessage = (index: number, field: keyof ChatMessage, value: any) => {
    const updatedMessages = [...messages];
    updatedMessages[index] = { ...updatedMessages[index], [field]: value };
    setMessages(updatedMessages);
    setValue('items', updatedMessages);
  };

  const removeMessage = (index: number) => {
    const updatedMessages = messages.filter((_, i) => i !== index);
    setMessages(updatedMessages);
    setValue('items', updatedMessages);
  };

  const parseJsonInput = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      if (Array.isArray(parsed)) {
        setMessages(parsed);
        setValue('items', parsed);
        toast.success(`Loaded ${parsed.length} messages from JSON`);
      } else {
        toast.error('JSON must be an array of messages');
      }
    } catch (error) {
      toast.error('Invalid JSON format');
    }
  };

  const exportJson = () => {
    const json = JSON.stringify(messages, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const onSubmit = (data: ChatIngestFormData) => {
    ingestMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Ingest Chat Messages</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Platform Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Platform</label>
              <div className="grid gap-3 md:grid-cols-2">
                {platformOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedPlatform === option.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => setValue('platform', option.value)}
                  >
                    <div>
                      <p className="font-medium">{option.label}</p>
                      <p className="text-sm text-muted-foreground">
                        {option.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* JSON Import/Export */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Import from JSON</label>
              <div className="space-y-3">
                <textarea
                  value={jsonInput}
                  onChange={(e) => setJsonInput(e.target.value)}
                  placeholder='[{"author": "User", "text": "Hello world", "timestamp": "2023-10-26T10:00:00Z"}]'
                  className="w-full min-h-[120px] p-3 border rounded-lg font-mono text-sm"
                />
                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={parseJsonInput}
                    disabled={!jsonInput.trim()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Import JSON
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={exportJson}
                    disabled={messages.length === 0}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Export JSON
                  </Button>
                </div>
              </div>
            </div>

            {/* Manual Message Entry */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Messages ({messages.length})</label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addMessage}
                >
                  Add Message
                </Button>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {messages.map((message, index) => (
                  <div key={index} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Message {index + 1}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeMessage(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid gap-3 md:grid-cols-2">
                      <div className="space-y-1">
                        <label className="text-xs text-muted-foreground">Author</label>
                        <Input
                          value={message.author || ''}
                          onChange={(e) => updateMessage(index, 'author', e.target.value)}
                          placeholder="Author name"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs text-muted-foreground">Timestamp</label>
                        <Input
                          value={message.timestamp}
                          onChange={(e) => updateMessage(index, 'timestamp', e.target.value)}
                          placeholder="2023-10-26T10:00:00Z"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs text-muted-foreground">Message Text</label>
                      <textarea
                        value={message.text}
                        onChange={(e) => updateMessage(index, 'text', e.target.value)}
                        placeholder="Message content..."
                        className="w-full min-h-[80px] p-3 border rounded-lg text-sm"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {messages.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No messages added yet. Click "Add Message" to get started.</p>
                </div>
              )}
            </div>

            {/* Metadata */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Metadata (Optional)</label>
              <textarea
                {...register('metadata')}
                placeholder='{"channel": "general", "team": "engineering"}'
                className="w-full min-h-[80px] p-3 border rounded-lg font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Additional metadata as JSON (optional)
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4">
              <Button
                type="submit"
                disabled={ingestMutation.isPending || messages.length === 0}
                className="flex-1"
              >
                {ingestMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing Chat...
                  </>
                ) : (
                  <>
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Ingest {messages.length} Message{messages.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
              
              {jobId && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push(`/processing?job_id=${jobId}`)}
                >
                  View Job
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Import chat exports directly from Slack, Discord, Teams, or other platforms
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Each message should have author, text, and timestamp fields
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Large chat exports may take time to process. Check job status for progress
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
