"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Network, Search, ZoomIn, ZoomOut, RotateCcw, Settings, Eye, EyeOff } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { GraphView } from "@/components/graph-view"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"

// Mock graph data
const mockGraphData = {
  nodes: [
    { id: "1", label: "Q4 Planning", group: "meeting", importance: 0.9, type: "pdf" },
    { id: "2", label: "AI Research", group: "research", importance: 0.8, type: "text" },
    { id: "3", label: "Customer Feedback", group: "feedback", importance: 0.7, type: "chat" },
    { id: "4", label: "Budget Allocation", group: "finance", importance: 0.6, type: "pdf" },
    { id: "5", label: "Team Structure", group: "hr", importance: 0.5, type: "text" },
    { id: "6", label: "Product Roadmap", group: "product", importance: 0.8, type: "web" },
    { id: "7", label: "Technical Specs", group: "technical", importance: 0.7, type: "pdf" },
    { id: "8", label: "User Stories", group: "product", importance: 0.6, type: "text" },
  ],
  links: [
    { source: "1", target: "4", strength: 0.8 },
    { source: "1", target: "5", strength: 0.6 },
    { source: "2", target: "7", strength: 0.9 },
    { source: "2", target: "6", strength: 0.7 },
    { source: "3", target: "8", strength: 0.8 },
    { source: "6", target: "8", strength: 0.7 },
    { source: "4", target: "5", strength: 0.5 },
    { source: "7", target: "8", strength: 0.6 },
  ]
}

const groupColors = {
  meeting: "bg-blue-500",
  research: "bg-green-500", 
  feedback: "bg-yellow-500",
  finance: "bg-red-500",
  hr: "bg-purple-500",
  product: "bg-indigo-500",
  technical: "bg-orange-500",
}

export default function GraphPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [graphSettings, setGraphSettings] = useState({
    showLabels: true,
    showConnections: true,
    nodeSize: 1,
    linkStrength: 0.5
  })

  // Mock API call for graph data
  const { data: graphData, isLoading } = useQuery({
    queryKey: ["graph-data", searchQuery],
    queryFn: async () => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (searchQuery) {
        // Filter nodes based on search query
        const filteredNodes = mockGraphData.nodes.filter(node => 
          node.label.toLowerCase().includes(searchQuery.toLowerCase())
        )
        const filteredNodeIds = filteredNodes.map(node => node.id)
        const filteredLinks = mockGraphData.links.filter(link => 
          filteredNodeIds.includes(link.source) && filteredNodeIds.includes(link.target)
        )
        
        return {
          nodes: filteredNodes,
          links: filteredLinks
        }
      }
      
      return mockGraphData
    }
  })

  const handleNodeClick = (node: any) => {
    setSelectedNode(node)
  }

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  const clearSearch = () => {
    setSearchQuery("")
    setSelectedNode(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Knowledge Graph
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Explore connections between your memories in 3D space.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Search and Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search for specific topics or concepts..."
                value={searchQuery}
                onChange={handleSearch}
                className="pl-10"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <ZoomIn className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <ZoomOut className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <RotateCcw className="w-4 h-4" />
              </Button>
              {searchQuery && (
                <Button variant="ghost" size="sm" onClick={clearSearch}>
                  Clear
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings Panel */}
      {showSettings && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Graph Settings</CardTitle>
              <CardDescription>
                Customize the appearance and behavior of the graph
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Node Size</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={graphSettings.nodeSize}
                    onChange={(e) => setGraphSettings(prev => ({ ...prev, nodeSize: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Link Strength</label>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={graphSettings.linkStrength}
                    onChange={(e) => setGraphSettings(prev => ({ ...prev, linkStrength: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={graphSettings.showLabels}
                    onChange={(e) => setGraphSettings(prev => ({ ...prev, showLabels: e.target.checked }))}
                  />
                  <span className="text-sm">Show Labels</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={graphSettings.showConnections}
                    onChange={(e) => setGraphSettings(prev => ({ ...prev, showConnections: e.target.checked }))}
                  />
                  <span className="text-sm">Show Connections</span>
                </label>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Graph and Details */}
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Graph View */}
        <div className="lg:col-span-3">
          <Card className="h-[600px]">
            <CardContent className="p-0 h-full">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4" />
                    <p className="text-slate-600 dark:text-slate-400">Loading graph...</p>
                  </div>
                </div>
              ) : (
                <GraphView
                  data={graphData}
                  onNodeClick={handleNodeClick}
                  settings={graphSettings}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Node Details */}
        <div className="space-y-4">
          {selectedNode ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">{selectedNode.label}</CardTitle>
                  <CardDescription>
                    <Badge 
                      variant="secondary" 
                      className={groupColors[selectedNode.group as keyof typeof groupColors]}
                    >
                      {selectedNode.group}
                    </Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-600 dark:text-slate-400">Type:</span>
                        <span>{selectedNode.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600 dark:text-slate-400">Importance:</span>
                        <span>{Math.round(selectedNode.importance * 100)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-2">Connections</h4>
                    <div className="space-y-1">
                      {graphData?.links
                        .filter(link => link.source === selectedNode.id || link.target === selectedNode.id)
                        .map((link, index) => {
                          const connectedNodeId = link.source === selectedNode.id ? link.target : link.source
                          const connectedNode = graphData?.nodes.find(node => node.id === connectedNodeId)
                          return (
                            <div key={index} className="text-sm text-slate-600 dark:text-slate-400">
                              • {connectedNode?.label} ({Math.round(link.strength * 100)}%)
                            </div>
                          )
                        })}
                    </div>
                  </div>
                  
                  <Button className="w-full" variant="outline">
                    View Full Memory
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <Network className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-semibold mb-2">Select a Node</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">
                  Click on any node in the graph to view its details and connections.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Graph Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Graph Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600 dark:text-slate-400">Nodes:</span>
                <span>{graphData?.nodes.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600 dark:text-slate-400">Connections:</span>
                <span>{graphData?.links.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600 dark:text-slate-400">Groups:</span>
                <span>{new Set(graphData?.nodes.map(node => node.group)).size || 0}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
