'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useUIStore } from '@/store/ui';
import { useChatStore } from '@/store/chat';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Loader2, 
  Bot, 
  User, 
  Settings,
  Plus,
  Trash2,
  Copy,
  ThumbsUp,
  ThumbsDown,
  ExternalLink
} from 'lucide-react';
import { Message, Memory, ModalityType } from '@/lib/types';
import { toast } from 'sonner';
import { formatRelativeTime } from '@/lib/format';

interface ChatWindowProps {
  className?: string;
}

export function ChatWindow({ className }: ChatWindowProps) {
  const { tenantId, userId } = useUIStore();
  const { 
    messages, 
    context, 
    isLoading, 
    addMessage, 
    updateLastMessage, 
    setContext, 
    setIsLoading,
    createSession,
    currentSessionId,
    getCurrentSession
  } = useChatStore();
  
  const [inputMessage, setInputMessage] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [retrievalSettings, setRetrievalSettings] = useState({
    modalities: [] as ModalityType[],
    k: 5,
    groundingRequired: true,
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async (userMessage: string) => {
      const chatMessages: Message[] = [
        ...messages,
        { role: 'user', content: userMessage }
      ];
      
      return api.chat({
        messages: chatMessages,
        retrieval_hints: {
          modalities: retrievalSettings.modalities.length > 0 ? retrievalSettings.modalities : undefined,
          k: retrievalSettings.k,
          filters: {},
        },
        temperature: 0.7,
      });
    },
    onSuccess: (response) => {
      // Add user message
      addMessage({ role: 'user', content: inputMessage });
      
      // Add assistant response with streaming effect
      const assistantMessage: Message = { role: 'assistant', content: '' };
      addMessage(assistantMessage);
      
      // Simulate streaming
      let currentText = '';
      const words = response.output.split(' ');
      
      const streamInterval = setInterval(() => {
        if (words.length === 0) {
          clearInterval(streamInterval);
          setContext(response.memories_used);
          setIsLoading(false);
          return;
        }
        
        currentText += words.shift() + ' ';
        updateLastMessage(currentText.trim());
      }, 50);
      
      setInputMessage('');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to get response');
      setIsLoading(false);
    },
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isLoading) return;
    
    setIsLoading(true);
    chatMutation.mutate(inputMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Message copied to clipboard');
  };

  const rateMessage = (messageId: string, rating: 'up' | 'down') => {
    // This would integrate with a feedback system
    toast.success(`Message rated ${rating}`);
  };

  const newChat = () => {
    createSession('New Chat');
    toast.success('New chat started');
  };

  const clearChat = () => {
    if (currentSessionId) {
      // This would clear the current session
      toast.success('Chat cleared');
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-3">
          <h2 className="text-lg font-semibold">Chat with Memories</h2>
          {context.length > 0 && (
            <Badge variant="secondary">
              {context.length} memories in context
            </Badge>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={newChat}
          >
            <Plus className="h-4 w-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={clearChat}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-4 border-b bg-muted/50">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="text-sm font-medium mb-2 block">Memory Count</label>
              <Input
                type="number"
                min="1"
                max="20"
                value={retrievalSettings.k}
                onChange={(e) => setRetrievalSettings(prev => ({
                  ...prev,
                  k: parseInt(e.target.value) || 5
                }))}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Modalities</label>
              <div className="flex flex-wrap gap-1">
                {['text', 'web', 'pdf', 'image', 'video', 'chat'].map((modality) => (
                  <Badge
                    key={modality}
                    variant={retrievalSettings.modalities.includes(modality as ModalityType) ? 'default' : 'outline'}
                    className="cursor-pointer text-xs"
                    onClick={() => {
                      const modalities = retrievalSettings.modalities.includes(modality as ModalityType)
                        ? retrievalSettings.modalities.filter(m => m !== modality)
                        : [...retrievalSettings.modalities, modality as ModalityType];
                      setRetrievalSettings(prev => ({ ...prev, modalities }));
                    }}
                  >
                    {modality}
                  </Badge>
                ))}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="grounding"
                checked={retrievalSettings.groundingRequired}
                onChange={(e) => setRetrievalSettings(prev => ({
                  ...prev,
                  groundingRequired: e.target.checked
                }))}
                className="rounded"
              />
              <label htmlFor="grounding" className="text-sm font-medium">
                Require grounding
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
            <p className="text-muted-foreground">
              Ask questions about your memories and get AI-powered answers
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex space-x-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                message.role === 'user' 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-muted text-muted-foreground'
              }`}>
                {message.role === 'user' ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>
              
              <Card className={`${message.role === 'user' ? 'bg-primary text-primary-foreground' : ''}`}>
                <CardContent className="p-4">
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-border/50">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyMessage(message.content)}
                        className="h-6 w-6 p-0"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => rateMessage(`msg-${index}`, 'up')}
                        className="h-6 w-6 p-0"
                      >
                        <ThumbsUp className="h-3 w-3" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => rateMessage(`msg-${index}`, 'down')}
                        className="h-6 w-6 p-0"
                      >
                        <ThumbsDown className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex space-x-3">
              <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Context Panel */}
      {context.length > 0 && (
        <div className="p-4 border-t bg-muted/30">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium">Memories Used</h4>
            <Badge variant="outline" className="text-xs">
              {context.length} memories
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2">
            {context.slice(0, 5).map((memory, index) => (
              <Badge
                key={memory.id}
                variant="secondary"
                className="cursor-pointer text-xs"
                onClick={() => {
                  // This would open the memory in a modal or side panel
                  toast.success(`Memory: ${memory.text.slice(0, 50)}...`);
                }}
              >
                {memory.modality} • {(memory as any).score ? ((memory as any).score * 100).toFixed(0) + '%' : 'N/A'}
              </Badge>
            ))}
            {context.length > 5 && (
              <Badge variant="outline" className="text-xs">
                +{context.length - 5} more
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your memories..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
