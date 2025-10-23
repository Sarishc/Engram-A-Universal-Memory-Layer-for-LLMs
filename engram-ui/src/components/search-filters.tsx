"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Calendar, Filter, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface SearchFiltersProps {
  filters: {
    modalities: string[]
    dateRange: { start: string; end: string } | null
    importanceThreshold: number
  }
  onFiltersChange: (filters: any) => void
}

const modalities = [
  { id: "pdf", label: "PDF", color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" },
  { id: "text", label: "Text", color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" },
  { id: "chat", label: "Chat", color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" },
  { id: "web", label: "Web", color: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200" },
  { id: "image", label: "Image", color: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200" },
  { id: "video", label: "Video", color: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200" },
]

export function SearchFilters({ filters, onFiltersChange }: SearchFiltersProps) {
  const [showDatePicker, setShowDatePicker] = useState(false)

  const toggleModality = (modality: string) => {
    const newModalities = filters.modalities.includes(modality)
      ? filters.modalities.filter(m => m !== modality)
      : [...filters.modalities, modality]
    
    onFiltersChange({
      ...filters,
      modalities: newModalities
    })
  }

  const setDateRange = (start: string, end: string) => {
    onFiltersChange({
      ...filters,
      dateRange: { start, end }
    })
  }

  const clearDateRange = () => {
    onFiltersChange({
      ...filters,
      dateRange: null
    })
  }

  const setImportanceThreshold = (threshold: number) => {
    onFiltersChange({
      ...filters,
      importanceThreshold: threshold
    })
  }

  const clearAllFilters = () => {
    onFiltersChange({
      modalities: [],
      dateRange: null,
      importanceThreshold: 0
    })
  }

  const hasActiveFilters = filters.modalities.length > 0 || filters.dateRange || filters.importanceThreshold > 0

  return (
    <div className="space-y-4">
      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="flex items-center space-x-2 flex-wrap">
          <span className="text-sm font-medium">Active filters:</span>
          {filters.modalities.map(modality => (
            <Badge
              key={modality}
              variant="secondary"
              className="cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700"
              onClick={() => toggleModality(modality)}
            >
              {modalities.find(m => m.id === modality)?.label}
              <X className="w-3 h-3 ml-1" />
            </Badge>
          ))}
          {filters.dateRange && (
            <Badge
              variant="secondary"
              className="cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700"
              onClick={clearDateRange}
            >
              Date Range
              <X className="w-3 h-3 ml-1" />
            </Badge>
          )}
          {filters.importanceThreshold > 0 && (
            <Badge
              variant="secondary"
              className="cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700"
              onClick={() => setImportanceThreshold(0)}
            >
              Importance: {Math.round(filters.importanceThreshold * 100)}%
              <X className="w-3 h-3 ml-1" />
            </Badge>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          >
            Clear all
          </Button>
        </div>
      )}

      {/* Filter Options */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Content Types */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Content Types</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {modalities.map(modality => (
              <Button
                key={modality.id}
                variant="ghost"
                size="sm"
                className={cn(
                  "w-full justify-start text-sm",
                  filters.modalities.includes(modality.id)
                    ? "bg-slate-100 dark:bg-slate-800"
                    : "hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
                onClick={() => toggleModality(modality.id)}
              >
                <div className={cn("w-2 h-2 rounded-full mr-2", modality.color)} />
                {modality.label}
              </Button>
            ))}
          </CardContent>
        </Card>

        {/* Date Range */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Date Range</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start"
              onClick={() => setShowDatePicker(!showDatePicker)}
            >
              <Calendar className="w-4 h-4 mr-2" />
              {filters.dateRange ? "Custom Range" : "Select Date Range"}
            </Button>
            
            {showDatePicker && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-700"
              >
                <div>
                  <label className="text-xs text-slate-600 dark:text-slate-400">From</label>
                  <Input
                    type="date"
                    size="sm"
                    value={filters.dateRange?.start || ""}
                    onChange={(e) => setDateRange(e.target.value, filters.dateRange?.end || "")}
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-600 dark:text-slate-400">To</label>
                  <Input
                    type="date"
                    size="sm"
                    value={filters.dateRange?.end || ""}
                    onChange={(e) => setDateRange(filters.dateRange?.start || "", e.target.value)}
                  />
                </div>
              </motion.div>
            )}

            {/* Quick Date Options */}
            <div className="space-y-1">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => {
                  const today = new Date()
                  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
                  setDateRange(weekAgo.toISOString().split('T')[0], today.toISOString().split('T')[0])
                }}
              >
                Last 7 days
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => {
                  const today = new Date()
                  const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
                  setDateRange(monthAgo.toISOString().split('T')[0], today.toISOString().split('T')[0])
                }}
              >
                Last 30 days
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Importance Threshold */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Importance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400">
                <span>Any</span>
                <span>{Math.round(filters.importanceThreshold * 100)}%</span>
                <span>Critical</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={filters.importanceThreshold}
                onChange={(e) => setImportanceThreshold(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
            
            <div className="space-y-1">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => setImportanceThreshold(0.8)}
              >
                High Importance (80%+)
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => setImportanceThreshold(0.6)}
              >
                Medium+ (60%+)
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => setImportanceThreshold(0)}
              >
                All Content
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
