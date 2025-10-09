'use client';

import { useState } from 'react';
import { useUIStore } from '@/store/ui';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Settings as SettingsIcon, 
  User, 
  Key, 
  Globe,
  Moon,
  Sun,
  Save,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export default function SettingsPage() {
  const { 
    theme, 
    toggleTheme, 
    tenantId, 
    userId, 
    setUserContext 
  } = useUIStore();
  
  const [localTenantId, setLocalTenantId] = useState(tenantId);
  const [localUserId, setLocalUserId] = useState(userId);
  const [apiBaseUrl, setApiBaseUrl] = useState(process.env.NEXT_PUBLIC_ENGRAM_API_BASE || 'http://localhost:8000');
  const [apiKey, setApiKey] = useState(process.env.NEXT_PUBLIC_ENGRAM_API_KEY || '');

  const handleSaveUserContext = () => {
    if (localTenantId.trim() && localUserId.trim()) {
      setUserContext(localTenantId.trim(), localUserId.trim());
      toast.success('User context updated successfully');
    } else {
      toast.error('Please enter both tenant ID and user ID');
    }
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/v1/health`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });
      
      if (response.ok) {
        toast.success('Connection successful');
      } else {
        toast.error('Connection failed');
      }
    } catch (error) {
      toast.error('Connection failed');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Settings</h1>
        <p className="text-muted-foreground">
          Configure your Engram experience
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* User Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>User Context</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Tenant ID</label>
              <Input
                value={localTenantId}
                onChange={(e) => setLocalTenantId(e.target.value)}
                placeholder="your-tenant-id"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">User ID</label>
              <Input
                value={localUserId}
                onChange={(e) => setLocalUserId(e.target.value)}
                placeholder="your-user-id"
              />
            </div>
            
            <Button onClick={handleSaveUserContext} className="w-full">
              <Save className="h-4 w-4 mr-2" />
              Save User Context
            </Button>
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Key className="h-5 w-5" />
              <span>API Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">API Base URL</label>
              <Input
                value={apiBaseUrl}
                onChange={(e) => setApiBaseUrl(e.target.value)}
                placeholder="http://localhost:8000"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">API Key</label>
              <Input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="your-api-key"
              />
            </div>
            
            <div className="flex space-x-2">
              <Button onClick={testConnection} variant="outline" className="flex-1">
                Test Connection
              </Button>
              <Button onClick={() => {
                setApiBaseUrl(process.env.NEXT_PUBLIC_ENGRAM_API_BASE || 'http://localhost:8000');
                setApiKey(process.env.NEXT_PUBLIC_ENGRAM_API_KEY || '');
                toast.success('Reset to defaults');
              }} variant="outline" className="flex-1">
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Theme Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
              <span>Appearance</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Theme</label>
              <div className="flex space-x-2">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  onClick={() => theme !== 'light' && toggleTheme()}
                  className="flex-1"
                >
                  <Sun className="h-4 w-4 mr-2" />
                  Light
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  onClick={() => theme !== 'dark' && toggleTheme()}
                  className="flex-1"
                >
                  <Moon className="h-4 w-4 mr-2" />
                  Dark
                </Button>
              </div>
            </div>
            
            <div className="text-sm text-muted-foreground">
              <p>Choose your preferred theme. Changes are applied immediately.</p>
            </div>
          </CardContent>
        </Card>

        {/* System Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5" />
              <span>System Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">App Version</span>
                <Badge variant="outline">1.0.0</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Version</span>
                <Badge variant="outline">v1</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Environment</span>
                <Badge variant="outline">
                  {process.env.NODE_ENV || 'development'}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Connection Status</span>
                <div className="flex items-center space-x-1">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm text-green-600">Connected</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Advanced Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <SettingsIcon className="h-5 w-5" />
            <span>Advanced Settings</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-2 block">Cache Duration</label>
              <select className="w-full p-2 border rounded-lg">
                <option>5 minutes</option>
                <option>15 minutes</option>
                <option>30 minutes</option>
                <option>1 hour</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Request Timeout</label>
              <select className="w-full p-2 border rounded-lg">
                <option>10 seconds</option>
                <option>30 seconds</option>
                <option>60 seconds</option>
                <option>5 minutes</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Max Retries</label>
              <select className="w-full p-2 border rounded-lg">
                <option>1</option>
                <option>3</option>
                <option>5</option>
                <option>10</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Debug Mode</label>
              <div className="flex items-center space-x-2">
                <input type="checkbox" className="rounded" />
                <span className="text-sm">Enable debug logging</span>
              </div>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button>
              <Save className="h-4 w-4 mr-2" />
              Save Settings
            </Button>
            <Button variant="outline">
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-medium">Export Data</h4>
              <p className="text-sm text-muted-foreground">
                Download your memories and settings
              </p>
              <Button variant="outline" className="w-full">
                Export All Data
              </Button>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Clear Cache</h4>
              <p className="text-sm text-muted-foreground">
                Clear local cache and temporary data
              </p>
              <Button variant="outline" className="w-full">
                Clear Cache
              </Button>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Reset Settings</h4>
              <p className="text-sm text-muted-foreground">
                Reset all settings to defaults
              </p>
              <Button variant="outline" className="w-full">
                Reset Settings
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
