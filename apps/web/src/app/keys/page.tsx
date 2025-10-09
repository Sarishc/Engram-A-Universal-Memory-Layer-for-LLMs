'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Key, 
  Plus, 
  Eye, 
  EyeOff, 
  Copy, 
  Trash2, 
  CheckCircle,
  AlertCircle,
  Calendar,
  User,
  Loader2
} from 'lucide-react';
import { SCOPES } from '@/lib/constants';
import { toast } from 'sonner';
import { formatRelativeTime } from '@/lib/format';

interface CreateKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (key: { id: string; key: string }) => void;
}

function CreateKeyModal({ isOpen, onClose, onSuccess }: CreateKeyModalProps) {
  const [name, setName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);

  const createKeyMutation = useMutation({
    mutationFn: () => api.createKey({
      name,
      scopes: selectedScopes,
    }),
    onSuccess: (response) => {
      onSuccess(response);
      onClose();
      setName('');
      setSelectedScopes([]);
    },
    onError: (error: any) => {
      toast.error(`Failed to create key: ${error.message}`);
    },
  });

  const toggleScope = (scope: string) => {
    setSelectedScopes(prev => 
      prev.includes(scope) 
        ? prev.filter(s => s !== scope)
        : [...prev, scope]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create API Key</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My API Key"
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Scopes</label>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {SCOPES.map((scope) => (
                <label key={scope.value} className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedScopes.includes(scope.value)}
                    onChange={() => toggleScope(scope.value)}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium text-sm">{scope.label}</div>
                    <div className="text-xs text-muted-foreground">{scope.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex space-x-2">
            <Button
              onClick={() => createKeyMutation.mutate()}
              disabled={!name.trim() || selectedScopes.length === 0}
              className="flex-1"
            >
              {createKeyMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Create Key'
              )}
            </Button>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface KeyRevealModalProps {
  isOpen: boolean;
  keyData: { id: string; key: string } | null;
  onClose: () => void;
}

function KeyRevealModal({ isOpen, keyData, onClose }: KeyRevealModalProps) {
  const [showKey, setShowKey] = useState(false);

  const copyKey = () => {
    if (keyData) {
      navigator.clipboard.writeText(keyData.key);
      toast.success('API key copied to clipboard');
    }
  };

  if (!isOpen || !keyData) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span>API Key Created</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-yellow-600" />
              <p className="text-sm text-yellow-800">
                This is the only time you'll see this key. Make sure to copy it now.
              </p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Your API Key</label>
            <div className="flex space-x-2">
              <Input
                value={showKey ? keyData.key : '••••••••••••••••••••••••••••••••'}
                readOnly
                className="font-mono"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          <div className="flex space-x-2">
            <Button onClick={copyKey} className="flex-1">
              <Copy className="h-4 w-4 mr-2" />
              Copy Key
            </Button>
            <Button variant="outline" onClick={onClose}>
              Done
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function KeysPage() {
  const queryClient = useQueryClient();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [revealModalOpen, setRevealModalOpen] = useState(false);
  const [newKeyData, setNewKeyData] = useState<{ id: string; key: string } | null>(null);

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: queryKeys.apiKeys,
    queryFn: api.listKeys,
  });

  const deleteKeyMutation = useMutation({
    mutationFn: (keyId: string) => api.deleteKey(keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.apiKeys });
      toast.success('API key deleted successfully');
    },
    onError: (error: any) => {
      toast.error(`Failed to delete key: ${error.message}`);
    },
  });

  const handleCreateKey = (keyData: { id: string; key: string }) => {
    setNewKeyData(keyData);
    setRevealModalOpen(true);
    queryClient.invalidateQueries({ queryKey: queryKeys.apiKeys });
  };

  const maskKey = (key: string) => {
    return key.slice(0, 8) + '••••••••••••••••••••••••••••••••';
  };

  const getScopeBadges = (scopes: string[]) => {
    return scopes.map(scope => {
      const scopeInfo = SCOPES.find(s => s.value === scope);
      return (
        <Badge key={scope} variant="outline" className="text-xs">
          {scopeInfo?.label || scope}
        </Badge>
      );
    });
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">API Keys</h1>
          <p className="text-muted-foreground">
            Manage API keys for programmatic access to your knowledge base
          </p>
        </div>
        
        <Button onClick={() => setCreateModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Key
        </Button>
      </div>

      {/* API Keys List */}
      <Card>
        <CardHeader>
          <CardTitle>Your API Keys</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-muted rounded-lg" />
                </div>
              ))}
            </div>
          ) : apiKeys && apiKeys.length > 0 ? (
            <div className="space-y-4">
              {apiKeys.map((key) => (
                <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Key className="h-4 w-4 text-muted-foreground" />
                      <h3 className="font-medium">{key.name}</h3>
                      <Badge variant={key.active ? 'default' : 'secondary'}>
                        {key.active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">Key:</span>
                        <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                          {maskKey(key.id)}
                        </code>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">Scopes:</span>
                        <div className="flex flex-wrap gap-1">
                          {getScopeBadges(key.scopes)}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>Created {formatRelativeTime(key.created_at)}</span>
                        </div>
                        
                        {key.last_used_at && (
                          <div className="flex items-center space-x-1">
                            <User className="h-3 w-3" />
                            <span>Last used {formatRelativeTime(key.last_used_at)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteKeyMutation.mutate(key.id)}
                      disabled={deleteKeyMutation.isPending}
                    >
                      {deleteKeyMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Key className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No API Keys</h3>
              <p className="text-muted-foreground mb-4">
                Create your first API key to start using the API
              </p>
              <Button onClick={() => setCreateModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create API Key
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>API Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Authentication</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Include your API key in the request header:
              </p>
              <code className="block bg-muted p-2 rounded text-sm">
                X-API-Key: your-api-key-here
              </code>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Base URL</h4>
              <code className="block bg-muted p-2 rounded text-sm">
                {process.env.NEXT_PUBLIC_ENGRAM_API_BASE || 'http://localhost:8000'}/v1
              </code>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Example Request</h4>
              <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`curl -X POST \\
  ${process.env.NEXT_PUBLIC_ENGRAM_API_BASE || 'http://localhost:8000'}/v1/memories/retrieve \\
  -H "X-API-Key: your-api-key-here" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "machine learning",
    "top_k": 10
  }'`}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modals */}
      <CreateKeyModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={handleCreateKey}
      />
      
      <KeyRevealModal
        isOpen={revealModalOpen}
        keyData={newKeyData}
        onClose={() => setRevealModalOpen(false)}
      />
    </div>
  );
}
