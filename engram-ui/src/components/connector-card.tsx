"use client"

import { motion } from "framer-motion"
import { CheckCircle, AlertCircle, ExternalLink, Settings, RefreshCw, Trash2, Loader2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

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

interface ConnectorCardProps {
  connector: Connector
  onConnect: () => void
  onDisconnect: () => void
  onSync: () => void
  isConnecting: boolean
  isDisconnecting: boolean
  isSyncing: boolean
}

export function ConnectorCard({
  connector,
  onConnect,
  onDisconnect,
  onSync,
  isConnecting,
  isDisconnecting,
  isSyncing
}: ConnectorCardProps) {
  const getStatusIcon = () => {
    switch (connector.status) {
      case "connected":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <div className="w-4 h-4 rounded-full bg-slate-300" />
    }
  }

  const getStatusColor = () => {
    switch (connector.status) {
      case "connected":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200"
    }
  }

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      <Card className="h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg", connector.color)}>
                {connector.icon}
              </div>
              <div>
                <CardTitle className="text-lg">{connector.name}</CardTitle>
                <CardDescription className="text-sm">
                  {connector.category}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon()}
              <Badge variant="secondary" className={getStatusColor()}>
                {connector.status}
              </Badge>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {connector.description}
          </p>

          {/* Stats */}
          {connector.status === "connected" && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">Items synced:</span>
                <span className="font-medium">{connector.itemCount?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">Last sync:</span>
                <span className="font-medium">{connector.lastSync}</span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col space-y-2">
            {connector.status === "connected" ? (
              <>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onSync}
                    disabled={isSyncing}
                    className="flex-1"
                  >
                    {isSyncing ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4 mr-2" />
                    )}
                    {isSyncing ? "Syncing..." : "Sync Now"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onDisconnect}
                    disabled={isDisconnecting}
                    className="flex-1"
                  >
                    {isDisconnecting ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4 mr-2" />
                    )}
                    {isDisconnecting ? "Disconnecting..." : "Disconnect"}
                  </Button>
                </div>
                <Button variant="ghost" size="sm" className="w-full">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </>
            ) : (
              <Button
                variant="gradient"
                onClick={onConnect}
                disabled={isConnecting}
                className="w-full"
              >
                {isConnecting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <ExternalLink className="w-4 h-4 mr-2" />
                )}
                {isConnecting ? "Connecting..." : "Connect"}
              </Button>
            )}
          </div>

          {/* Error State */}
          {connector.status === "error" && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">
                Connection failed. Please try reconnecting.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
