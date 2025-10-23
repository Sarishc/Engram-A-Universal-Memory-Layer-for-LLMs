"use client"

import { useState, useCallback } from "react"
import { motion } from "framer-motion"
import { Upload, FileText, Link, Type, X, CheckCircle, AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { FileUpload } from "@/components/file-upload"
import { useDropzone } from "react-dropzone"
import { useMutation } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { toast } from "sonner"

interface UploadJob {
  id: string
  filename: string
  status: "queued" | "processing" | "completed" | "failed"
  progress: number
  error?: string
}

export default function UploadPage() {
  const [activeTab, setActiveTab] = useState<"file" | "url" | "text">("file")
  const [url, setUrl] = useState("")
  const [text, setText] = useState("")
  const [uploadJobs, setUploadJobs] = useState<UploadJob[]>([])

  // Mock tenant and user IDs - in real app, these would come from auth context
  const tenantId = "demo-tenant"
  const userId = "demo-user"

  const uploadFileMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.uploadFile(file, tenantId, userId)
      return response
    },
    onSuccess: (data) => {
      toast.success("File uploaded successfully!")
      setUploadJobs(prev => [...prev, {
        id: data.job_id,
        filename: "uploaded-file",
        status: data.status,
        progress: 0
      }])
    },
    onError: (error) => {
      toast.error("Upload failed: " + error.message)
    }
  })

  const uploadUrlMutation = useMutation({
    mutationFn: async (url: string) => {
      const response = await apiClient.uploadUrl(url, tenantId, userId)
      return response
    },
    onSuccess: (data) => {
      toast.success("URL submitted successfully!")
      setUploadJobs(prev => [...prev, {
        id: data.job_id,
        filename: url,
        status: data.status,
        progress: 0
      }])
      setUrl("")
    },
    onError: (error) => {
      toast.error("URL upload failed: " + error.message)
    }
  })

  const uploadTextMutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await apiClient.uploadText(text, tenantId, userId)
      return response
    },
    onSuccess: (data) => {
      toast.success("Text submitted successfully!")
      setUploadJobs(prev => [...prev, {
        id: data.job_id,
        filename: "text-input",
        status: data.status,
        progress: 0
      }])
      setText("")
    },
    onError: (error) => {
      toast.error("Text upload failed: " + error.message)
    }
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      uploadFileMutation.mutate(file)
    })
  }, [uploadFileMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: true
  })

  const handleUrlSubmit = () => {
    if (!url.trim()) return
    uploadUrlMutation.mutate(url)
  }

  const handleTextSubmit = () => {
    if (!text.trim()) return
    uploadTextMutation.mutate(text)
  }

  const removeJob = (jobId: string) => {
    setUploadJobs(prev => prev.filter(job => job.id !== jobId))
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Upload Content
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Add files, URLs, or text to your memory system.
        </p>
      </div>

      {/* Upload Tabs */}
      <Card>
        <CardHeader>
          <CardTitle>Choose Upload Method</CardTitle>
          <CardDescription>
            Select how you want to add content to your memory system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-1 mb-6 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
            {[
              { id: "file", label: "File Upload", icon: FileText },
              { id: "url", label: "URL", icon: Link },
              { id: "text", label: "Text", icon: Type },
            ].map((tab) => (
              <Button
                key={tab.id}
                variant={activeTab === tab.id ? "default" : "ghost"}
                className="flex-1 justify-start"
                onClick={() => setActiveTab(tab.id as any)}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </Button>
            ))}
          </div>

          {/* File Upload */}
          {activeTab === "file" && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300
                  ${isDragActive 
                    ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950" 
                    : "border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                  }
                `}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-semibold mb-2">
                  {isDragActive ? "Drop files here" : "Drag & drop files here"}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  or click to browse files
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {[".pdf", ".txt", ".md", ".doc", ".docx"].map((ext) => (
                    <Badge key={ext} variant="secondary">{ext}</Badge>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* URL Upload */}
          {activeTab === "url" && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium mb-2">
                  Website URL
                </label>
                <div className="flex space-x-2">
                  <Input
                    placeholder="https://example.com/article"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleUrlSubmit}
                    disabled={!url.trim() || uploadUrlMutation.isPending}
                    variant="gradient"
                  >
                    {uploadUrlMutation.isPending ? "Processing..." : "Add URL"}
                  </Button>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Engram will extract and process the content from the webpage.
              </p>
            </motion.div>
          )}

          {/* Text Upload */}
          {activeTab === "text" && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium mb-2">
                  Text Content
                </label>
                <textarea
                  placeholder="Paste your text content here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="w-full h-32 px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div className="flex justify-between items-center">
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {text.length} characters
                </p>
                <Button 
                  onClick={handleTextSubmit}
                  disabled={!text.trim() || uploadTextMutation.isPending}
                  variant="gradient"
                >
                  {uploadTextMutation.isPending ? "Processing..." : "Add Text"}
                </Button>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Upload Jobs */}
      {uploadJobs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Queue</CardTitle>
            <CardDescription>
              Files and content being processed by AI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {uploadJobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center space-x-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{job.filename}</span>
                    <div className="flex items-center space-x-2">
                      {job.status === "completed" && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                      {job.status === "failed" && (
                        <AlertCircle className="w-4 h-4 text-red-500" />
                      )}
                      <Badge 
                        variant={job.status === "completed" ? "success" : job.status === "failed" ? "destructive" : "info"}
                      >
                        {job.status}
                      </Badge>
                    </div>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                  {job.error && (
                    <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                      {job.error}
                    </p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeJob(job.id)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
