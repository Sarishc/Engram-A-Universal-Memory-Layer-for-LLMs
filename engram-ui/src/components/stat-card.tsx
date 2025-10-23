"use client"

import { motion } from "framer-motion"
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface StatCardProps {
  title: string
  value: string
  icon: LucideIcon
  trend?: string
  trendDirection?: "up" | "down" | "neutral"
  className?: string
}

export function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendDirection = "neutral",
  className 
}: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      <Card className={cn("h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm", className)}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {trend && (
                <div className="flex items-center space-x-1">
                  {trendDirection === "up" && (
                    <TrendingUp className="w-4 h-4 text-green-500" />
                  )}
                  {trendDirection === "down" && (
                    <TrendingDown className="w-4 h-4 text-red-500" />
                  )}
                  <span className={cn(
                    "text-sm font-medium",
                    trendDirection === "up" && "text-green-600",
                    trendDirection === "down" && "text-red-600",
                    trendDirection === "neutral" && "text-muted-foreground"
                  )}>
                    {trend}
                  </span>
                </div>
              )}
            </div>
            <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
              <Icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
