'use client';

import { GraphCanvas } from '@/components/graph/GraphCanvas';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Network, 
  Search, 
  Settings,
  Eye,
  EyeOff,
  Info
} from 'lucide-react';

export default function GraphPage() {
  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Knowledge Graph</h1>
          <p className="text-muted-foreground">
            Explore the connections between your memories and concepts
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Network className="h-3 w-3" />
            <span>Interactive</span>
          </Badge>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Graph Canvas */}
        <div className="flex-1">
          <GraphCanvas />
        </div>

        {/* Sidebar */}
        <div className="w-80 border-l bg-card flex flex-col">
          {/* Graph Info */}
          <div className="p-4 border-b">
            <h3 className="font-semibold mb-3">Graph Information</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total Nodes</span>
                <Badge variant="secondary">0</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total Edges</span>
                <Badge variant="secondary">0</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Connected Components</span>
                <Badge variant="secondary">0</Badge>
              </div>
            </div>
          </div>

          {/* Graph Controls */}
          <div className="p-4 border-b">
            <h3 className="font-semibold mb-3">Controls</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium mb-2 block">Layout Algorithm</label>
                <select className="w-full p-2 border rounded-lg text-sm">
                  <option>Force-directed</option>
                  <option>Hierarchical</option>
                  <option>Circular</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Node Size</label>
                <input
                  type="range"
                  min="5"
                  max="20"
                  defaultValue="10"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Edge Thickness</label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  defaultValue="2"
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="p-4 border-b">
            <h3 className="font-semibold mb-3">Filters</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium mb-2 block">Node Types</label>
                <div className="space-y-2">
                  {['concept', 'entity', 'document', 'person'].map((type) => (
                    <label key={type} className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked className="rounded" />
                      <span className="text-sm">{type}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Edge Types</label>
                <div className="space-y-2">
                  {['contains', 'relates_to', 'references', 'similar_to'].map((type) => (
                    <label key={type} className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked className="rounded" />
                      <span className="text-sm">{type}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Searches */}
          <div className="p-4 border-b">
            <h3 className="font-semibold mb-3">Recent Searches</h3>
            <div className="space-y-2">
              {['machine learning', 'artificial intelligence', 'neural networks'].map((search) => (
                <div key={search} className="flex items-center space-x-2 p-2 hover:bg-accent/50 rounded cursor-pointer">
                  <Search className="h-3 w-3 text-muted-foreground" />
                  <span className="text-sm">{search}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Help */}
          <div className="p-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-sm">
                  <Info className="h-4 w-4" />
                  <span>Tips</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2">
                <p>• Click and drag to pan around the graph</p>
                <p>• Scroll to zoom in and out</p>
                <p>• Click nodes to see details</p>
                <p>• Use the search to find specific entities</p>
                <p>• Adjust filters to focus on specific types</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
