'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/store/ui';
import { NAVIGATION_ITEMS, KEYBOARD_SHORTCUTS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronLeft, 
  ChevronRight, 
  Brain, 
  Home,
  Download,
  Search,
  MessageSquare,
  Network,
  Link2,
  BarChart3,
  Key,
  Settings,
  Cog
} from 'lucide-react';

const iconMap = {
  '🏠': Home,
  '📥': Download,
  '🔍': Search,
  '💬': MessageSquare,
  '🕸️': Network,
  '🔗': Link2,
  '📊': BarChart3,
  '🔑': Key,
  '⚙️': Cog,
  '🔧': Settings,
};

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  return (
    <div
      className={cn(
        'flex h-full flex-col border-r bg-card transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        <div className={cn(
          'flex items-center space-x-3 transition-opacity duration-300',
          sidebarCollapsed ? 'opacity-0 w-0' : 'opacity-100'
        )}>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-semibold">Engram</span>
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="h-8 w-8 shrink-0"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {NAVIGATION_ITEMS.map((item) => {
          const Icon = iconMap[item.icon as keyof typeof iconMap] || Home;
          const active = isActive(item.href);
          
          return (
            <Link key={item.id} href={item.href}>
              <div
                className={cn(
                  'group relative flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 hover:bg-accent',
                  active 
                    ? 'bg-accent text-accent-foreground' 
                    : 'text-muted-foreground hover:text-accent-foreground',
                  sidebarCollapsed && 'justify-center px-2'
                )}
                onMouseEnter={() => setHoveredItem(item.id)}
                onMouseLeave={() => setHoveredItem(null)}
              >
                <Icon className="h-5 w-5 shrink-0" />
                
                {!sidebarCollapsed && (
                  <span className="truncate">{item.title}</span>
                )}

                {/* Tooltip for collapsed state */}
                {sidebarCollapsed && hoveredItem === item.id && (
                  <div className="absolute left-full ml-2 z-50 rounded-md bg-popover px-3 py-2 text-sm font-medium text-popover-foreground shadow-md">
                    {item.title}
                    <div className="absolute left-0 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rotate-45 bg-popover" />
                  </div>
                )}

                {/* Keyboard shortcut badge */}
                {!sidebarCollapsed && item.id === 'search' && (
                  <Badge variant="outline" className="ml-auto text-xs">
                    {KEYBOARD_SHORTCUTS.search}
                  </Badge>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className={cn(
          'space-y-2 transition-opacity duration-300',
          sidebarCollapsed ? 'opacity-0' : 'opacity-100'
        )}>
          <div className="text-xs text-muted-foreground">
            Keyboard shortcuts
          </div>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Search</span>
              <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                <span className="text-xs">{KEYBOARD_SHORTCUTS.search}</span>
              </kbd>
            </div>
            <div className="flex justify-between">
              <span>Ingest</span>
              <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                <span className="text-xs">{KEYBOARD_SHORTCUTS.openIngest}</span>
              </kbd>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
