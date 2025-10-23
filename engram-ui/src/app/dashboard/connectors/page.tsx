"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Globe, CheckCircle, AlertCircle, ExternalLink, Settings, RefreshCw, Trash2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ConnectorCard } from "@/components/connector-card"
import { useQuery, useMutation } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { toast } from "sonner"

interface Connector {
  id: string
  name: string
  description: string
  icon: string
  status: "connected" | "disconnected" | "error"
  lastSync?: string
  itemCount?: number
  color: string
  category: string
}

const mockConnectors: Connector[] = [
  {
    id: "google-drive",
    name: "Google Drive",
    description: "Sync files and documents from your Google Drive",
    icon: "📁",
    status: "connected",
    lastSync: "2 hours ago",
    itemCount: 1247,
    color: "bg-blue-500",
    category: "Storage"
  },
  {
    id: "notion",
    name: "Notion",
    description: "Import pages and databases from Notion",
    icon: "📝",
    status: "connected",
    lastSync: "1 hour ago",
    itemCount: 89,
    color: "bg-gray-500",
    category: "Productivity"
  },
  {
    id: "slack",
    name: "Slack",
    description: "Sync messages and files from Slack channels",
    icon: "💬",
    status: "disconnected",
    lastSync: "3 days ago",
    itemCount: 0,
    color: "bg-purple-500",
    category: "Communication"
  },
  {
    id: "github",
    name: "GitHub",
    description: "Import repositories, issues, and documentation",
    icon: "⚡",
    status: "error",
    lastSync: "1 week ago",
    itemCount: 0,
    color: "bg-gray-800",
    category: "Development"
  },
  {
    id: "chrome",
    name: "Chrome Extension",
    description: "Save web pages and articles as you browse",
    icon: "🌐",
    status: "disconnected",
    lastSync: "Never",
    itemCount: 0,
    color: "bg-green-500",
    category: "Browser"
  },
  {
    id: "discord",
    name: "Discord",
    description: "Sync messages and files from Discord servers",
    icon: "🎮",
    status: "disconnected",
    lastSync: "Never",
    itemCount: 0,
    color: "bg-indigo-500",
    category: "Communication"
  }
]

export default function ConnectorsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all")

  const { data: connectors } = useQuery({
    queryKey: ["connectors"],
    queryFn: () => Promise.resolve(mockConnectors),
  })

  const connectMutation = useMutation({
    mutationFn: async (connectorId: string) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      return { success: true }
    },
    onSuccess: (_, connectorId) => {
      toast.success(`${connectorId} connected successfully!`)
    },
    onError: (error) => {
      toast.error("Connection failed: " + error.message)
    }
  })

  const disconnectMutation = useMutation({
    mutationFn: async (connectorId: string) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      return { success: true }
    },
    onSuccess: (_, connectorId) => {
      toast.success(`${connectorId} disconnected successfully!`)
    },
    onError: (error) => {
      toast.error("Disconnection failed: " + error.message)
    }
  })

  const syncMutation = useMutation({
    mutationFn: async (connectorId: string) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      return { success: true }
    },
    onSuccess: (_, connectorId) => {
      toast.success(`${connectorId} synced successfully!`)
    },
    onError: (error) => {
      toast.error("Sync failed: " + error.message)
    }
  })

  const categories = ["all", ...Array.from(new Set(connectors?.map(c => c.category) || []))]

  const filteredConnectors = connectors?.filter(connector => 
    selectedCategory === "all" || connector.category === selectedCategory
  ) || []

  const connectedCount = connectors?.filter(c => c.status === "connected").length || 0
  const totalItems = connectors?.reduce((sum, c) => sum + (c.itemCount || 0), 0) || 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Connectors
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Connect your favorite tools and services to automatically sync content.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold">{connectedCount}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400">Connected</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-600 flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalItems.toLocaleString()}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400">Total Items</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-purple-500 to-pink-600 flex items-center justify-center">
                <RefreshCw className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold">Auto</p>
                <p className="text-sm text-slate-600 dark:text-slate-400">Sync Mode</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <Button
            key={category}
            variant={selectedCategory === category ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(category)}
            className="capitalize"
          >
            {category}
          </Button>
        ))}
      </div>

      {/* Connectors Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredConnectors.map((connector, index) => (
          <motion.div
            key={connector.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <ConnectorCard
              connector={connector}
              onConnect={() => connectMutation.mutate(connector.id)}
              onDisconnect={() => disconnectMutation.mutate(connector.id)}
              onSync={() => syncMutation.mutate(connector.id)}
              isConnecting={connectMutation.isPending}
              isDisconnecting={disconnectMutation.isPending}
              isSyncing={syncMutation.isPending}
            />
          </motion.div>
        ))}
      </div>

      {/* Setup Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Setup Instructions
          </CardTitle>
          <CardDescription>
            Learn how to connect and configure your integrations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Getting Started</h4>
              <ul className="space-y-1 text-sm text-slate-600 dark:text-slate-400">
                <li>• Click "Connect" on any service above</li>
                <li>• Authorize Engram to access your data</li>
                <li>• Configure sync settings and filters</li>
                <li>• Start syncing content automatically</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Best Practices</h4>
              <ul className="space-y-1 text-sm text-slate-600 dark:text-slate-400">
                <li>• Start with one or two connectors</li>
                <li>• Use filters to avoid syncing everything</li>
                <li>• Regularly check sync status</li>
                <li>• Review privacy settings for each service</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
