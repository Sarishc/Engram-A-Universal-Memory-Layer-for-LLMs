"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { User, Key, Bell, Palette, Shield, Database, Download, Trash2, Eye, EyeOff } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useTheme } from "next-themes"
import { toast } from "sonner"

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey, setApiKey] = useState("eng_sk_1234567890abcdef")
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sync: false
  })

  const handleExportData = () => {
    toast.success("Data export started. You'll receive an email when ready.")
  }

  const handleDeleteAccount = () => {
    toast.error("Account deletion requires confirmation. Please contact support.")
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Settings
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Manage your account, preferences, and system settings.
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="w-5 h-5 mr-2" />
                  Personal Information
                </CardTitle>
                <CardDescription>
                  Update your personal details and contact information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <Input defaultValue="John Doe" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <Input defaultValue="john@example.com" type="email" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Company</label>
                  <Input defaultValue="Acme Corp" />
                </div>
                <Button>Save Changes</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Account Information</CardTitle>
                <CardDescription>
                  Your account details and subscription status
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Account Status</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Plan</span>
                  <Badge variant="secondary">Pro</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Member Since</span>
                  <span className="text-sm text-slate-600 dark:text-slate-400">Jan 2024</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Storage Used</span>
                  <span className="text-sm text-slate-600 dark:text-slate-400">2.3 GB / 10 GB</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Key className="w-5 h-5 mr-2" />
                  API Keys
                </CardTitle>
                <CardDescription>
                  Manage your API keys for programmatic access
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">API Key</label>
                  <div className="flex space-x-2">
                    <Input
                      type={showApiKey ? "text" : "password"}
                      value={apiKey}
                      readOnly
                      className="font-mono"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Keep your API key secure and never share it publicly
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline">Regenerate</Button>
                  <Button variant="outline">Copy</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Security Settings
                </CardTitle>
                <CardDescription>
                  Configure security and privacy settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Two-Factor Authentication</span>
                    <Button variant="outline" size="sm">Enable</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Login Notifications</span>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Session Timeout</span>
                    <Badge variant="secondary">24 hours</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Choose how you want to be notified about activities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Receive updates via email
                    </p>
                  </div>
                  <Button
                    variant={notifications.email ? "default" : "outline"}
                    size="sm"
                    onClick={() => setNotifications(prev => ({ ...prev, email: !prev.email }))}
                  >
                    {notifications.email ? "Enabled" : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Push Notifications</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Browser and mobile push notifications
                    </p>
                  </div>
                  <Button
                    variant={notifications.push ? "default" : "outline"}
                    size="sm"
                    onClick={() => setNotifications(prev => ({ ...prev, push: !prev.push }))}
                  >
                    {notifications.push ? "Enabled" : "Disabled"}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Sync Notifications</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Notify when connectors finish syncing
                    </p>
                  </div>
                  <Button
                    variant={notifications.sync ? "default" : "outline"}
                    size="sm"
                    onClick={() => setNotifications(prev => ({ ...prev, sync: !prev.sync }))}
                  >
                    {notifications.sync ? "Enabled" : "Disabled"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Palette className="w-5 h-5 mr-2" />
                Theme & Appearance
              </CardTitle>
              <CardDescription>
                Customize the look and feel of your interface
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-4">Theme</h4>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { id: "light", label: "Light", icon: "☀️" },
                    { id: "dark", label: "Dark", icon: "🌙" },
                    { id: "system", label: "System", icon: "💻" }
                  ].map((themeOption) => (
                    <Button
                      key={themeOption.id}
                      variant={theme === themeOption.id ? "default" : "outline"}
                      className="flex flex-col items-center space-y-2 h-20"
                      onClick={() => setTheme(themeOption.id)}
                    >
                      <span className="text-2xl">{themeOption.icon}</span>
                      <span className="text-sm">{themeOption.label}</span>
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-4">Display Settings</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Compact Mode</span>
                    <Button variant="outline" size="sm">Disabled</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Animations</span>
                    <Button variant="default" size="sm">Enabled</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Sidebar Position</span>
                    <Badge variant="secondary">Left</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Tab */}
        <TabsContent value="data">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Data Management
                </CardTitle>
                <CardDescription>
                  Export, import, and manage your data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={handleExportData}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export All Data
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Database className="w-4 h-4 mr-2" />
                    Download Memories
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Database className="w-4 h-4 mr-2" />
                    Download Graph Data
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trash2 className="w-5 h-5 mr-2" />
                  Danger Zone
                </CardTitle>
                <CardDescription>
                  Irreversible actions that affect your account
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full justify-start text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear All Memories
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-red-600 hover:text-red-700"
                    onClick={handleDeleteAccount}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Account
                  </Button>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  These actions cannot be undone. Please proceed with caution.
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Configure advanced system settings and integrations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">API Base URL</label>
                  <Input defaultValue="https://api.engram.ai" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Sync Frequency</label>
                  <select className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800">
                    <option>Every 15 minutes</option>
                    <option>Every hour</option>
                    <option>Every 6 hours</option>
                    <option>Daily</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Debug Mode</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Enable detailed logging and debugging
                    </p>
                  </div>
                  <Button variant="outline" size="sm">Disabled</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
