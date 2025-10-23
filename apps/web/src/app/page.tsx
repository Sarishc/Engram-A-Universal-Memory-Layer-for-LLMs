'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { useUIStore } from '@/store/ui';
import { StatCard } from '@/components/common/StatCard';
import { EmptyState } from '@/components/common/EmptyState';
import { SkeletonCard } from '@/components/common/Skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  FileText, 
  Network, 
  Activity,
  Plus,
  Globe,
  Upload,
  MessageSquare,
  Search,
  TrendingUp,
  Clock,
  AlertCircle
} from 'lucide-react';

export default function Dashboard() {
  const router = useRouter();
  const { tenantId } = useUIStore();

  // Fetch analytics data
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: queryKeys.analyticsOverview(tenantId || '', useUIStore.getState().userId || ''),
    queryFn: () => api.analyticsOverview(tenantId || '', useUIStore.getState().userId || ''),
    enabled: !!tenantId,
  });

  // Fetch recent memories
  const { data: recentMemories, isLoading: memoriesLoading } = useQuery({
    queryKey: queryKeys.memoriesList({ limit: 5, tenant_id: tenantId }),
    queryFn: () => api.listMemories({ 
      limit: 5, 
      tenant_id: tenantId,
      user_id: useUIStore.getState().userId 
    }),
    enabled: !!tenantId,
  });

  // Fetch recent jobs
  const { data: recentJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', 'recent', tenantId],
    queryFn: async () => {
      // This would be a real API call in production
      return [];
    },
    enabled: !!tenantId,
  });

  const quickActions = [
    {
      title: 'Ingest URL',
      description: 'Add web content to your memory',
      icon: Globe,
      onClick: () => router.push('/ingest?tab=url'),
      color: 'bg-blue-500',
    },
    {
      title: 'Upload File',
      description: 'Upload documents, images, or videos',
      icon: Upload,
      onClick: () => router.push('/ingest?tab=file'),
      color: 'bg-green-500',
    },
    {
      title: 'Start Chat',
      description: 'Chat with your memories',
      icon: MessageSquare,
      onClick: () => router.push('/chat'),
      color: 'bg-purple-500',
    },
    {
      title: 'Explore Graph',
      description: 'Visualize knowledge connections',
      icon: Network,
      onClick: () => router.push('/graph'),
      color: 'bg-orange-500',
    },
  ];

  if (analyticsLoading || memoriesLoading || jobsLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Welcome to Engram</h1>
            <p className="text-muted-foreground">Your AI-powered second brain</p>
          </div>
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Welcome to Engram</h1>
          <p className="text-muted-foreground">Your AI-powered second brain</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>Connected</span>
          </Badge>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Memories"
          value={analytics?.total_requests || 0}
          description="All stored memories"
          icon={<Brain className="h-4 w-4" />}
          trend={analytics ? {
            value: analytics.requests_last_24h,
            label: `+${analytics.requests_last_24h} today`,
            isPositive: true,
          } : undefined}
        />
        <StatCard
          title="Documents"
          value={recentMemories?.total_count || 0}
          description="Processed documents"
          icon={<FileText className="h-4 w-4" />}
        />
        <StatCard
          title="Connections"
          value="0"
          description="Graph relationships"
          icon={<Network className="h-4 w-4" />}
        />
        <StatCard
          title="P95 Latency"
          value={`${analytics?.p95_latency_ms || 0}ms`}
          description="Response time"
          icon={<Activity className="h-4 w-4" />}
          trend={analytics ? {
            value: -5,
            label: '5ms faster',
            isPositive: true,
          } : undefined}
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>Quick Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action) => (
              <Button
                key={action.title}
                variant="outline"
                className="h-auto p-4 flex flex-col items-start space-y-2"
                onClick={action.onClick}
              >
                <div className="flex items-center space-x-2">
                  <div className={`p-2 rounded-lg ${action.color} text-white`}>
                    <action.icon className="h-4 w-4" />
                  </div>
                  <span className="font-medium">{action.title}</span>
                </div>
                <span className="text-sm text-muted-foreground text-left">
                  {action.description}
                </span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Jobs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Recent Jobs</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentJobs && recentJobs.length > 0 ? (
              <div className="space-y-3">
                {recentJobs.map((job: any) => (
                  <div key={job.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      <div className="h-2 w-2 rounded-full bg-green-500" />
                      <div>
                        <p className="font-medium">{job.type}</p>
                        <p className="text-sm text-muted-foreground">
                          {job.status}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline">
                      {job.progress}%
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={<AlertCircle className="h-8 w-8" />}
                title="No recent jobs"
                description="Jobs will appear here as you ingest content"
                action={{
                  label: 'Start Ingesting',
                  onClick: () => router.push('/ingest'),
                }}
              />
            )}
          </CardContent>
        </Card>

        {/* Recent Memories */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Recent Memories</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentMemories && recentMemories.memories.length > 0 ? (
              <div className="space-y-3">
                {recentMemories.memories.map((memory) => (
                  <div key={memory.id} className="p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">
                          {memory.text.slice(0, 50)}...
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {memory.modality}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(memory.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={<Brain className="h-8 w-8" />}
                title="No memories yet"
                description="Start by ingesting some content to build your knowledge base"
                action={{
                  label: 'Add Content',
                  onClick: () => router.push('/ingest'),
                }}
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div>
                <p className="font-medium">API Server</p>
                <p className="text-sm text-muted-foreground">Online</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div>
                <p className="font-medium">Vector Database</p>
                <p className="text-sm text-muted-foreground">Connected</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div>
                <p className="font-medium">Job Queue</p>
                <p className="text-sm text-muted-foreground">Active</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
