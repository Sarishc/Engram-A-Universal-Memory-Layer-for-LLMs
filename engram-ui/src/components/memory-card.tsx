"use client"

import { motion } from "framer-motion"
import { FileText, Calendar, Tag, ExternalLink } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Memory } from "@/lib/api"
import { formatRelativeTime, getFileTypeIcon } from "@/lib/utils"
import { cn } from "@/lib/utils"

interface MemoryCardProps {
  memory: Memory
  className?: string
}

export function MemoryCard({ memory, className }: MemoryCardProps) {
  const getModalityColor = (modality: string) => {
    switch (modality) {
      case "pdf":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      case "text":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "chat":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "web":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
      case "image":
        return "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200"
      case "video":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  const getImportanceColor = (importance: number) => {
    if (importance >= 0.8) return "bg-red-500"
    if (importance >= 0.6) return "bg-yellow-500"
    return "bg-green-500"
  }

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      <Card className={cn("border-0 shadow-sm hover:shadow-md transition-all duration-300 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm", className)}>
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getFileTypeIcon(memory.source)}</span>
                <Badge variant="secondary" className={getModalityColor(memory.modality)}>
                  {memory.modality}
                </Badge>
                <div className={cn("w-2 h-2 rounded-full", getImportanceColor(memory.importance))} />
              </div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <Calendar className="w-3 h-3" />
                <span>{formatRelativeTime(memory.created_at)}</span>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-2">
              <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-3">
                {memory.text}
              </p>
              
              {/* Tags */}
              {memory.tags && memory.tags.length > 0 && (
                <div className="flex items-center space-x-1 flex-wrap">
                  <Tag className="w-3 h-3 text-muted-foreground" />
                  {memory.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {memory.tags.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{memory.tags.length - 3}
                    </Badge>
                  )}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" className="h-8 px-2">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  View
                </Button>
                <Button variant="ghost" size="sm" className="h-8 px-2">
                  <FileText className="w-3 h-3 mr-1" />
                  Details
                </Button>
              </div>
              <div className="text-xs text-muted-foreground">
                {Math.round(memory.importance * 100)}% importance
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
