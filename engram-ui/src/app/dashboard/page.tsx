"use client"

import { motion } from "framer-motion"
import { Brain, Search, Upload, Network, TrendingUp, Clock, FileText, Users } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { MemoryCard } from "@/components/memory-card"
import { StatCard } from "@/components/stat-card"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import Link from "next/link"

// Mock data for demo
const mockStats = {
  totalMemories: 1247,
  totalEmbeddings: 8934,
  storageUsed: 2.3,
  lastActivity: "2 hours ago"
}

const mockRecentMemories = [
  {
    id: "1",
    text: "Meeting notes from Q4 planning session. Key decisions: focus on AI integration, expand to enterprise market, hire 5 new engineers.",
    metadata: { source: "meeting-notes.pdf", importance: 0.9 },
    created_at: "2024-01-15T10:30:00Z",
    tags: ["meeting", "planning", "Q4"],
    modality: "pdf" as const
  },
  {
    id: "2", 
    text: "Research on transformer architectures for long-context understanding. Key papers: Longformer, BigBird, and recent work on sparse attention patterns.",
    metadata: { source: "research-notes.md", importance: 0.8 },
    created_at: "2024-01-14T15:45:00Z",
    tags: ["research", "AI", "transformers"],
    modality: "text" as const
  },
  {
    id: "3",
    text: "Customer feedback from beta testing. Users love the search functionality but want better mobile experience.",
    metadata: { source: "feedback-slack", importance: 0.7 },
    created_at: "2024-01-14T09:20:00Z",
    tags: ["feedback", "beta", "mobile"],
    modality: "chat" as const
  }
]

const mockProcessingJobs = [
  { id: "1", filename: "quarterly-report.pdf", status: "processing", progress: 75 },
  { id: "2", filename: "research-paper.pdf", status: "queued", progress: 0 },
  { id: "3", filename: "meeting-recording.mp4", status: "completed", progress: 100 }
]

export default function DashboardPage() {
  // Mock API calls - in real app, these would be actual API calls
  const { data: stats } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => Promise.resolve(mockStats),
  })

  const { data: recentMemories } = useQuery({
    queryKey: ["recent-memories"],
    queryFn: () => Promise.resolve(mockRecentMemories),
  })

  const { data: processingJobs } = useQuery({
    queryKey: ["processing-jobs"],
    queryFn: () => Promise.resolve(mockProcessingJobs),
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Welcome back! 👋
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Here's what's happening with your memory system.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Memories"
          value={stats?.totalMemories.toLocaleString() || "0"}
          icon={Brain}
          trend="+12%"
          trendDirection="up"
        />
        <StatCard
          title="Embeddings"
          value={stats?.totalEmbeddings.toLocaleString() || "0"}
          icon={Search}
          trend="+8%"
          trendDirection="up"
        />
        <StatCard
          title="Storage Used"
          value={`${stats?.storageUsed || 0} GB`}
          icon={FileText}
          trend="+2.1%"
          trendDirection="up"
        />
        <StatCard
          title="Last Activity"
          value={stats?.lastActivity || "Never"}
          icon={Clock}
          trend="Active"
          trendDirection="neutral"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Recent Memories */}
        <div className="lg:col-span-2">
          <Card className="h-fit">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Memories</CardTitle>
                  <CardDescription>
                    Your latest uploaded and processed content
                  </CardDescription>
                </div>
                <Button asChild variant="outline" size="sm">
                  <Link href="/dashboard/search">View All</Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentMemories?.map((memory, index) => (
                <motion.div
                  key={memory.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <MemoryCard memory={memory} />
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Processing Status */}
        <div className="space-y-6">
          {/* Processing Jobs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Upload className="w-5 h-5 mr-2" />
                Processing Queue
              </CardTitle>
              <CardDescription>
                Files being processed by AI
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {processingJobs?.map((job, index) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="space-y-2"
                >
                  <div className="flex items-center justify-between text-sm">
                    <span className="truncate font-medium">{job.filename}</span>
                    <Badge 
                      variant={job.status === "completed" ? "success" : job.status === "processing" ? "info" : "secondary"}
                    >
                      {job.status}
                    </Badge>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                </motion.div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks and shortcuts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild variant="gradient" className="w-full justify-start">
                <Link href="/dashboard/upload">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Files
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link href="/dashboard/search">
                  <Search className="w-4 h-4 mr-2" />
                  Search Memories
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link href="/dashboard/graph">
                  <Network className="w-4 h-4 mr-2" />
                  View Graph
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* System Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">API Health</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Vector DB</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Processing</span>
                <Badge variant="info">Active</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
