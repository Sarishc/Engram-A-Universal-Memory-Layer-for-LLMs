'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useHotkeys } from 'react-hotkeys-hook';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/store/ui';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Plus, 
  Bell, 
  Settings, 
  User,
  Moon,
  Sun,
  ChevronDown,
  Activity
} from 'lucide-react';

interface TopbarProps {
  className?: string;
}

export function Topbar({ className }: TopbarProps) {
  const router = useRouter();
  const { 
    theme, 
    toggleTheme, 
    tenantId, 
    userId, 
    searchQuery, 
    setSearchQuery 
  } = useUIStore();
  
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Keyboard shortcuts
  useHotkeys('cmd+k, ctrl+k', (e) => {
    e.preventDefault();
    router.push('/search');
  });

  useHotkeys('cmd+i, ctrl+i', (e) => {
    e.preventDefault();
    router.push('/ingest');
  });

  useHotkeys('cmd+b, ctrl+b', (e) => {
    e.preventDefault();
    useUIStore.getState().toggleSidebar();
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const getBreadcrumb = () => {
    if (typeof window === 'undefined') return 'Dashboard';
    const path = window.location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    if (segments.length === 0) return 'Dashboard';
    
    const lastSegment = segments[segments.length - 1];
    return lastSegment.charAt(0).toUpperCase() + lastSegment.slice(1);
  };

  return (
    <header className={cn(
      'flex h-16 items-center justify-between border-b bg-background px-6',
      className
    )}>
      {/* Left section */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">{getBreadcrumb()}</span>
            <span className="text-xs text-muted-foreground">
              {tenantId && userId ? `${tenantId} • ${userId}` : 'Not connected'}
            </span>
          </div>
        </div>
      </div>

      {/* Center section - Search */}
      <div className="flex-1 max-w-md mx-8">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search memories... (⌘K)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
            className={cn(
              'pl-10 pr-4 transition-all duration-200',
              isSearchFocused && 'ring-2 ring-ring ring-offset-2'
            )}
          />
          {searchQuery && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setSearchQuery('')}
              className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 p-0"
            >
              ×
            </Button>
          )}
        </form>
      </div>

      {/* Right section */}
      <div className="flex items-center space-x-2">
        {/* Quick actions */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/ingest')}
          className="hidden sm:flex"
        >
          <Plus className="h-4 w-4 mr-2" />
          Ingest
        </Button>

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="h-9 w-9"
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 relative"
        >
          <Bell className="h-4 w-4" />
          <Badge 
            variant="destructive" 
            className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
          >
            3
          </Badge>
        </Button>

        {/* User menu */}
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            className="h-9 px-3"
          >
            <User className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">User</span>
            <ChevronDown className="h-3 w-3 ml-2" />
          </Button>
        </div>

        {/* Settings */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/settings')}
          className="h-9 w-9"
        >
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
