"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Sidebar } from "@/components/sidebar"
import { Topbar } from "@/components/topbar"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-indigo-950 dark:via-slate-900 dark:to-purple-950">
      <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />
      <div className="lg:pl-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="p-6"
        >
          {children}
        </motion.main>
      </div>
    </div>
  )
}
