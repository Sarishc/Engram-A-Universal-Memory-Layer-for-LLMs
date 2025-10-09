'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { useUIStore } from '@/store/ui';
import { StatCard } from '@/components/common/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/common/Skeleton';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Clock,
  Users,
  Database,
  Activity,
  AlertTriangle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

export default function AnalyticsPage() {
  const { tenantId } = useUIStore();

  const { data: analytics, isLoading } = useQuery({
    queryKey: queryKeys.analytics(tenantId || ''),
    queryFn: () => api.analyticsOverview(tenantId || ''),
    enabled: !!tenantId,
  });

  // Mock data for charts
  const latencyData = [
    { date: '2023-10-20', latency: 120 },
    { date: '2023-10-21', latency: 135 },
    { date: '2023-10-22', latency: 110 },
    { date: '2023-10-23', latency: 145 },
    { date: '2023-10-24', latency: 130 },
    { date: '2023-10-25', latency: 125 },
    { date: '2023-10-26', latency: 140 },
  ];

  const usageData = [
    { route: '/v1/memories/retrieve', requests: 1250, tokens: 45000 },
    { route: '/v1/chat', requests: 890, tokens: 32000 },
    { route: '/v1/ingest/file', requests: 45, tokens: 0 },
    { route: '/v1/ingest/url', requests: 78, tokens: 0 },
    { route: '/v1/graph/subgraph', requests: 234, tokens: 12000 },
  ];

  const modalityData = [
    { name: 'Text', value: 45, color: '#3b82f6' },
    { name: 'Web', value: 25, color: '#10b981' },
    { name: 'PDF', value: 15, color: '#ef4444' },
    { name: 'Image', value: 10, color: '#8b5cf6' },
    { name: 'Video', value: 5, color: '#f59e0b' },
  ];

  const statusCodeData = [
    { code: '200', count: 2150, percentage: 85 },
    { code: '400', count: 180, percentage: 7 },
    { code: '401', count: 95, percentage: 4 },
    { code: '500', count: 75, percentage: 3 },
    { code: '429', count: 50, percentage: 1 },
  ];

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">System performance and usage metrics</p>
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
          <h1 className="text-3xl font-bold gradient-text">Analytics</h1>
          <p className="text-muted-foreground">System performance and usage metrics</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Activity className="h-3 w-3" />
            <span>Real-time</span>
          </Badge>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Requests"
          value={analytics?.total_requests || 0}
          description="All API requests"
          icon={<Activity className="h-4 w-4" />}
          trend={analytics ? {
            value: analytics.requests_last_24h,
            label: `+${analytics.requests_last_24h} today`,
            isPositive: true,
          } : undefined}
        />
        
        <StatCard
          title="Avg Latency"
          value={`${analytics?.avg_latency_ms || 0}ms`}
          description="Response time"
          icon={<Clock className="h-4 w-4" />}
          trend={analytics ? {
            value: -5,
            label: '5ms faster',
            isPositive: true,
          } : undefined}
        />
        
        <StatCard
          title="P95 Latency"
          value={`${analytics?.p95_latency_ms || 0}ms`}
          description="95th percentile"
          icon={<AlertTriangle className="h-4 w-4" />}
        />
        
        <StatCard
          title="Success Rate"
          value="97.2%"
          description="Successful requests"
          icon={<TrendingUp className="h-4 w-4" />}
          trend={{
            value: 2.1,
            label: '+2.1% this week',
            isPositive: true,
          }}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Latency Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Response Time Trend</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={latencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="latency" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Usage by Route */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>API Usage by Route</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="route" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="requests" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Content Modalities */}
        <Card>
          <CardHeader>
            <CardTitle>Content Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={modalityData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {modalityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Codes */}
        <Card>
          <CardHeader>
            <CardTitle>Status Code Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {statusCodeData.map((status) => (
                <div key={status.code} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`h-3 w-3 rounded-full ${
                      status.code === '200' ? 'bg-green-500' :
                      status.code === '400' ? 'bg-yellow-500' :
                      status.code === '401' ? 'bg-orange-500' :
                      'bg-red-500'
                    }`} />
                    <span className="font-mono text-sm">{status.code}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{status.count}</div>
                    <div className="text-xs text-muted-foreground">{status.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Job Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Processing Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Total Jobs</span>
                <Badge variant="outline">{analytics?.ingest_jobs_total || 0}</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Pending</span>
                <Badge variant="secondary">{analytics?.ingest_jobs_pending || 0}</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Completed</span>
                <Badge variant="default">{analytics?.ingest_jobs_completed || 0}</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Failed</span>
                <Badge variant="destructive">{analytics?.ingest_jobs_failed || 0}</Badge>
              </div>
              
              <div className="pt-2 border-t">
                <div className="text-xs text-muted-foreground">
                  Success Rate: {analytics?.ingest_jobs_total ? 
                    ((analytics.ingest_jobs_completed / analytics.ingest_jobs_total) * 100).toFixed(1) 
                    : 0}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Entities and Sources */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Entities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: 'Machine Learning', count: 45, trend: '+12%' },
                { name: 'Artificial Intelligence', count: 38, trend: '+8%' },
                { name: 'Neural Networks', count: 32, trend: '+15%' },
                { name: 'Deep Learning', count: 28, trend: '+5%' },
                { name: 'Computer Vision', count: 22, trend: '+3%' },
              ].map((entity, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{entity.name}</p>
                    <p className="text-sm text-muted-foreground">{entity.count} mentions</p>
                  </div>
                  <Badge variant="outline" className="text-green-600">
                    {entity.trend}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: 'docs.google.com', count: 125, type: 'Web' },
                { name: 'arxiv.org', count: 89, type: 'Web' },
                { name: 'research-papers.pdf', count: 67, type: 'PDF' },
                { name: 'meeting-notes.txt', count: 45, type: 'Text' },
                { name: 'slack-export.json', count: 34, type: 'Chat' },
              ].map((source, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium truncate">{source.name}</p>
                    <p className="text-sm text-muted-foreground">{source.count} items</p>
                  </div>
                  <Badge variant="outline">{source.type}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
