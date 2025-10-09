import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message, Memory } from '@/lib/types';

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  context: Memory[];
  createdAt: Date;
  updatedAt: Date;
}

interface ChatState {
  // Current session
  currentSessionId: string | null;
  sessions: Record<string, ChatSession>;
  
  // Current chat state
  messages: Message[];
  context: Memory[];
  isLoading: boolean;
  
  // Actions
  createSession: (title?: string) => string;
  switchSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setContext: (memories: Memory[]) => void;
  clearContext: () => void;
  
  setIsLoading: (loading: boolean) => void;
  
  // Persistence
  saveCurrentSession: () => void;
  loadSession: (sessionId: string) => void;
  
  // Utility
  getCurrentSession: () => ChatSession | null;
  getSessionList: () => ChatSession[];
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Current session
      currentSessionId: null,
      sessions: {},
      
      // Current chat state
      messages: [],
      context: [],
      isLoading: false,
      
      // Actions
      createSession: (title) => {
        const sessionId = crypto.randomUUID();
        const now = new Date();
        
        const session: ChatSession = {
          id: sessionId,
          title: title || `Chat ${new Date().toLocaleDateString()}`,
          messages: [],
          context: [],
          createdAt: now,
          updatedAt: now,
        };
        
        set((state) => ({
          sessions: { ...state.sessions, [sessionId]: session },
          currentSessionId: sessionId,
          messages: [],
          context: [],
        }));
        
        return sessionId;
      },
      
      switchSession: (sessionId) => {
        const session = get().sessions[sessionId];
        if (session) {
          set({
            currentSessionId: sessionId,
            messages: session.messages,
            context: session.context,
          });
        }
      },
      
      deleteSession: (sessionId) => {
        set((state) => {
          const newSessions = { ...state.sessions };
          delete newSessions[sessionId];
          
          const isCurrentSession = state.currentSessionId === sessionId;
          
          return {
            sessions: newSessions,
            currentSessionId: isCurrentSession ? null : state.currentSessionId,
            messages: isCurrentSession ? [] : state.messages,
            context: isCurrentSession ? [] : state.context,
          };
        });
      },
      
      updateSessionTitle: (sessionId, title) => {
        set((state) => {
          const session = state.sessions[sessionId];
          if (session) {
            return {
              sessions: {
                ...state.sessions,
                [sessionId]: { ...session, title, updatedAt: new Date() }
              }
            };
          }
          return state;
        });
      },
      
      addMessage: (message) => {
        set((state) => {
          const newMessages = [...state.messages, message];
          
          // Update current session
          if (state.currentSessionId) {
            const session = state.sessions[state.currentSessionId];
            if (session) {
              return {
                messages: newMessages,
                sessions: {
                  ...state.sessions,
                  [state.currentSessionId]: {
                    ...session,
                    messages: newMessages,
                    updatedAt: new Date(),
                  }
                }
              };
            }
          }
          
          return { messages: newMessages };
        });
      },
      
      updateLastMessage: (content) => {
        set((state) => {
          const messages = [...state.messages];
          if (messages.length > 0) {
            messages[messages.length - 1] = {
              ...messages[messages.length - 1],
              content,
            };
          }
          
          // Update current session
          if (state.currentSessionId) {
            const session = state.sessions[state.currentSessionId];
            if (session) {
              return {
                messages,
                sessions: {
                  ...state.sessions,
                  [state.currentSessionId]: {
                    ...session,
                    messages,
                    updatedAt: new Date(),
                  }
                }
              };
            }
          }
          
          return { messages };
        });
      },
      
      setContext: (memories) => {
        set((state) => {
          // Update current session
          if (state.currentSessionId) {
            const session = state.sessions[state.currentSessionId];
            if (session) {
              return {
                context: memories,
                sessions: {
                  ...state.sessions,
                  [state.currentSessionId]: {
                    ...session,
                    context: memories,
                    updatedAt: new Date(),
                  }
                }
              };
            }
          }
          
          return { context: memories };
        });
      },
      
      clearContext: () => {
        set((state) => {
          // Update current session
          if (state.currentSessionId) {
            const session = state.sessions[state.currentSessionId];
            if (session) {
              return {
                context: [],
                sessions: {
                  ...state.sessions,
                  [state.currentSessionId]: {
                    ...session,
                    context: [],
                    updatedAt: new Date(),
                  }
                }
              };
            }
          }
          
          return { context: [] };
        });
      },
      
      setIsLoading: (loading) => set({ isLoading: loading }),
      
      saveCurrentSession: () => {
        const state = get();
        if (state.currentSessionId) {
          const session = state.sessions[state.currentSessionId];
          if (session) {
            set({
              sessions: {
                ...state.sessions,
                [state.currentSessionId]: {
                  ...session,
                  messages: state.messages,
                  context: state.context,
                  updatedAt: new Date(),
                }
              }
            });
          }
        }
      },
      
      loadSession: (sessionId) => {
        const session = get().sessions[sessionId];
        if (session) {
          set({
            currentSessionId: sessionId,
            messages: session.messages,
            context: session.context,
          });
        }
      },
      
      // Utility
      getCurrentSession: () => {
        const state = get();
        return state.currentSessionId ? state.sessions[state.currentSessionId] : null;
      },
      
      getSessionList: () => {
        return Object.values(get().sessions).sort(
          (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
        );
      },
    }),
    {
      name: 'engram-chat-store',
      partialize: (state) => ({
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
      }),
    }
  )
);
