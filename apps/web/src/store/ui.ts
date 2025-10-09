import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Layout
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  
  // Theme
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
  
  // User context
  tenantId: string;
  userId: string;
  setUserContext: (tenantId: string, userId: string) => void;
  
  // Modals
  modals: {
    createKey: boolean;
    deleteMemory: boolean;
    editMemory: boolean;
  };
  openModal: (modal: keyof UIState['modals']) => void;
  closeModal: (modal: keyof UIState['modals']) => void;
  closeAllModals: () => void;
  
  // Toasts
  toasts: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    description?: string;
    duration?: number;
  }>;
  addToast: (toast: Omit<UIState['toasts'][0], 'id'>) => void;
  removeToast: (id: string) => void;
  
  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  
  // Selected items
  selectedMemoryIds: string[];
  setSelectedMemoryIds: (ids: string[]) => void;
  toggleMemorySelection: (id: string) => void;
  clearSelection: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Layout
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      // Theme
      theme: 'dark',
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
      
      // User context
      tenantId: '',
      userId: '',
      setUserContext: (tenantId, userId) => set({ tenantId, userId }),
      
      // Modals
      modals: {
        createKey: false,
        deleteMemory: false,
        editMemory: false,
      },
      openModal: (modal) => set((state) => ({
        modals: { ...state.modals, [modal]: true }
      })),
      closeModal: (modal) => set((state) => ({
        modals: { ...state.modals, [modal]: false }
      })),
      closeAllModals: () => set({
        modals: {
          createKey: false,
          deleteMemory: false,
          editMemory: false,
        }
      }),
      
      // Toasts
      toasts: [],
      addToast: (toast) => {
        const id = crypto.randomUUID();
        set((state) => ({
          toasts: [...state.toasts, { ...toast, id }]
        }));
        
        // Auto-remove after duration
        const duration = toast.duration || 5000;
        setTimeout(() => {
          get().removeToast(id);
        }, duration);
      },
      removeToast: (id) => set((state) => ({
        toasts: state.toasts.filter((toast) => toast.id !== id)
      })),
      
      // Search
      searchQuery: '',
      setSearchQuery: (query) => set({ searchQuery: query }),
      
      // Selected items
      selectedMemoryIds: [],
      setSelectedMemoryIds: (ids) => set({ selectedMemoryIds: ids }),
      toggleMemorySelection: (id) => set((state) => {
        const isSelected = state.selectedMemoryIds.includes(id);
        return {
          selectedMemoryIds: isSelected
            ? state.selectedMemoryIds.filter((selectedId) => selectedId !== id)
            : [...state.selectedMemoryIds, id]
        };
      }),
      clearSelection: () => set({ selectedMemoryIds: [] }),
    }),
    {
      name: 'engram-ui-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
        tenantId: state.tenantId,
        userId: state.userId,
      }),
    }
  )
);
