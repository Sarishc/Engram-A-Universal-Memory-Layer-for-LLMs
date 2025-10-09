'use client';

import { useState } from 'react';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ContextPeek } from '@/components/chat/ContextPeek';
import { useChatStore } from '@/store/chat';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Brain, 
  Settings,
  History,
  Plus,
  Trash2,
  Star
} from 'lucide-react';

export default function ChatPage() {
  const { 
    currentSessionId,
    sessions,
    createSession,
    switchSession,
    deleteSession,
    getSessionList,
    getCurrentSession
  } = useChatStore();
  
  const [showSessions, setShowSessions] = useState(false);
  const sessionList = getSessionList();
  const currentSession = getCurrentSession();

  return (
    <div className="h-screen flex">
      {/* Sessions Sidebar */}
      {showSessions && (
        <div className="w-80 border-r bg-card flex flex-col">
          <div className="p-4 border-b">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Chat History</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowSessions(false)}
              >
                ×
              </Button>
            </div>
            
            <Button
              onClick={() => {
                createSession('New Chat');
                setShowSessions(false);
              }}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {sessionList.map((session) => (
                <Card
                  key={session.id}
                  className={`cursor-pointer transition-colors ${
                    currentSessionId === session.id ? 'bg-primary/10 border-primary' : 'hover:bg-accent/50'
                  }`}
                  onClick={() => {
                    switchSession(session.id);
                    setShowSessions(false);
                  }}
                >
                  <CardContent className="p-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-sm truncate">
                          {session.title}
                        </h3>
                        <p className="text-xs text-muted-foreground">
                          {session.messages.length} messages
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(session.updatedAt).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.id);
                        }}
                        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowSessions(true)}
            >
              <History className="h-4 w-4" />
            </Button>
            
            <div>
              <h1 className="text-lg font-semibold">Chat with Memories</h1>
              {currentSession && (
                <p className="text-sm text-muted-foreground">
                  {currentSession.title}
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="flex items-center space-x-1">
              <Brain className="h-3 w-3" />
              <span>RAG Enabled</span>
            </Badge>
          </div>
        </div>

        {/* Chat Window */}
        <div className="flex-1">
          <ChatWindow />
        </div>
      </div>
    </div>
  );
}
