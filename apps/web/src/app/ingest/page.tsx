'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UrlIngestForm } from '@/components/forms/UrlIngestForm';
import { FileIngestForm } from '@/components/forms/FileIngestForm';
import { ChatIngestForm } from '@/components/forms/ChatIngestForm';
import { 
  Globe, 
  Upload, 
  MessageSquare, 
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function IngestPage() {
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState('url');

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && ['url', 'file', 'chat'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Ingest Content</h1>
        <p className="text-muted-foreground">
          Add documents, web pages, images, videos, and chat messages to your knowledge base
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="url" className="flex items-center space-x-2">
                <Globe className="h-4 w-4" />
                <span>URL</span>
              </TabsTrigger>
              <TabsTrigger value="file" className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span>File</span>
              </TabsTrigger>
              <TabsTrigger value="chat" className="flex items-center space-x-2">
                <MessageSquare className="h-4 w-4" />
                <span>Chat</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-6">
              <TabsContent value="url">
                <UrlIngestForm />
              </TabsContent>
              <TabsContent value="file">
                <FileIngestForm />
              </TabsContent>
              <TabsContent value="chat">
                <ChatIngestForm />
              </TabsContent>
            </div>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Processing Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>Processing Timeline</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-xs font-bold text-primary-foreground">1</span>
                  </div>
                  <div>
                    <p className="font-medium">Upload</p>
                    <p className="text-sm text-muted-foreground">Content uploaded to server</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-xs font-bold text-primary">2</span>
                  </div>
                  <div>
                    <p className="font-medium">Processing</p>
                    <p className="text-sm text-muted-foreground">Extract text and metadata</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-xs font-bold text-primary">3</span>
                  </div>
                  <div>
                    <p className="font-medium">Chunking</p>
                    <p className="text-sm text-muted-foreground">Split content into chunks</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-xs font-bold text-primary">4</span>
                  </div>
                  <div>
                    <p className="font-medium">Embedding</p>
                    <p className="text-sm text-muted-foreground">Generate vector embeddings</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="text-xs font-bold text-primary">5</span>
                  </div>
                  <div>
                    <p className="font-medium">Storage</p>
                    <p className="text-sm text-muted-foreground">Save to vector database</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Ingestion Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  <strong>URL:</strong> Works with most web pages, PDFs, and direct file links
                </p>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  <strong>Files:</strong> Supports PDF, images, videos, and text files up to 100MB
                </p>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  <strong>Chat:</strong> Import from Slack, Discord, Teams, or manual entry
                </p>
              </div>
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  Processing time varies based on content size and complexity
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Supported Formats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Supported Formats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium mb-2">Documents</p>
                <div className="flex flex-wrap gap-1">
                  {['PDF', 'DOC', 'DOCX', 'TXT', 'MD'].map((format) => (
                    <Badge key={format} variant="outline" className="text-xs">
                      {format}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Images</p>
                <div className="flex flex-wrap gap-1">
                  {['PNG', 'JPG', 'JPEG', 'GIF', 'WebP'].map((format) => (
                    <Badge key={format} variant="outline" className="text-xs">
                      {format}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Videos</p>
                <div className="flex flex-wrap gap-1">
                  {['MP4', 'WebM', 'AVI', 'MOV'].map((format) => (
                    <Badge key={format} variant="outline" className="text-xs">
                      {format}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
