'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Link2, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Settings,
  RefreshCw,
  ExternalLink,
  Database
} from 'lucide-react';
import { CONNECTOR_TYPES } from '@/lib/constants';
import { toast } from 'sonner';

export default function ConnectorsPage() {
  const [connectingTo, setConnectingTo] = useState<string | null>(null);

  const syncMutation = useMutation({
    mutationFn: (connectorType: string) => {
      return api.syncConnector({
        source: connectorType,
        config: {},
      });
    },
    onSuccess: (response) => {
      toast.success(`${connectingTo} sync started successfully`);
      setConnectingTo(null);
    },
    onError: (error: any) => {
      toast.error(`Failed to sync ${connectingTo}: ${error.message}`);
      setConnectingTo(null);
    },
  });

  const handleConnect = (connectorType: string) => {
    setConnectingTo(connectorType);
    // In a real implementation, this would open OAuth flow
    toast.info(`Connecting to ${connectorType}...`);
    setTimeout(() => {
      setConnectingTo(null);
      toast.success(`Connected to ${connectorType}`);
    }, 2000);
  };

  const handleSync = (connectorType: string) => {
    setConnectingTo(connectorType);
    syncMutation.mutate(connectorType);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Connectors</h1>
        <p className="text-muted-foreground">
          Connect external services to automatically sync content into your knowledge base
        </p>
      </div>

      {/* Connector Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {CONNECTOR_TYPES.map((connector) => {
          const isConnecting = connectingTo === connector.id;
          const isConnected = Math.random() > 0.5; // Mock connection status
          
          return (
            <Card key={connector.id} className="relative">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{connector.icon}</div>
                    <div>
                      <CardTitle className="text-lg">{connector.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {connector.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {isConnected ? (
                      <Badge variant="default" className="bg-green-500">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Connected
                      </Badge>
                    ) : (
                      <Badge variant="outline">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Not Connected
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Connection Status */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Status</span>
                    <span className={isConnected ? 'text-green-600' : 'text-gray-500'}>
                      {isConnected ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  {isConnected && (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span>Last Sync</span>
                        <span className="text-muted-foreground">
                          {new Date().toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span>Items Synced</span>
                        <span className="text-muted-foreground">
                          {Math.floor(Math.random() * 100)}
                        </span>
                      </div>
                    </>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  {!isConnected ? (
                    <Button
                      onClick={() => handleConnect(connector.id)}
                      disabled={isConnecting}
                      className="flex-1"
                    >
                      {isConnecting ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Connecting...
                        </>
                      ) : (
                        <>
                          <Link2 className="h-4 w-4 mr-2" />
                          Connect
                        </>
                      )}
                    </Button>
                  ) : (
                    <>
                      <Button
                        variant="outline"
                        onClick={() => handleSync(connector.id)}
                        disabled={isConnecting}
                        className="flex-1"
                      >
                        {isConnecting ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <RefreshCw className="h-4 w-4" />
                        )}
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="icon"
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>

                {/* Connection Info */}
                {isConnected && (
                  <div className="pt-3 border-t">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Sync Frequency</span>
                      <span>Every 24 hours</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Auto-sync</span>
                      <span>Enabled</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Setup Guide */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Setup Guide</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-medium">Google Drive</h4>
              <ol className="text-sm text-muted-foreground space-y-1">
                <li>1. Click Connect to authorize access</li>
                <li>2. Select folders to sync</li>
                <li>3. Configure sync frequency</li>
                <li>4. Enable auto-sync</li>
              </ol>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Notion</h4>
              <ol className="text-sm text-muted-foreground space-y-1">
                <li>1. Create integration in Notion</li>
                <li>2. Share pages with integration</li>
                <li>3. Connect using integration token</li>
                <li>4. Select workspaces to sync</li>
              </ol>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Slack</h4>
              <ol className="text-sm text-muted-foreground space-y-1">
                <li>1. Install Slack app</li>
                <li>2. Authorize workspace access</li>
                <li>3. Select channels to sync</li>
                <li>4. Configure message filters</li>
              </ol>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sync Status */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Sync Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { connector: 'Google Drive', status: 'completed', time: '2 hours ago', items: 15 },
              { connector: 'Notion', status: 'completed', time: '4 hours ago', items: 8 },
              { connector: 'Slack', status: 'failed', time: '6 hours ago', items: 0 },
            ].map((sync, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`h-2 w-2 rounded-full ${
                    sync.status === 'completed' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="font-medium">{sync.connector}</p>
                    <p className="text-sm text-muted-foreground">
                      {sync.items} items • {sync.time}
                    </p>
                  </div>
                </div>
                
                <Badge variant={sync.status === 'completed' ? 'default' : 'destructive'}>
                  {sync.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
