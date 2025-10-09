'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from '@/lib/query';
import { useUIStore } from '@/store/ui';
import { GraphNode, GraphEdge, GraphData } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Settings,
  Eye,
  EyeOff,
  Network,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';

interface GraphCanvasProps {
  className?: string;
}

interface NodeTooltip {
  x: number;
  y: number;
  node: GraphNode;
}

export function GraphCanvas({ className }: GraphCanvasProps) {
  const { tenantId, userId } = useUIStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [tooltip, setTooltip] = useState<NodeTooltip | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [radius, setRadius] = useState(2);
  const [showLabels, setShowLabels] = useState(true);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock graph data for demonstration
  const mockGraphData: GraphData = {
    nodes: [
      {
        id: '1',
        label: 'Artificial Intelligence',
        type: 'concept',
        metadata: { importance: 0.9, modality: 'text' }
      },
      {
        id: '2',
        label: 'Machine Learning',
        type: 'concept',
        metadata: { importance: 0.8, modality: 'text' }
      },
      {
        id: '3',
        label: 'Neural Networks',
        type: 'concept',
        metadata: { importance: 0.7, modality: 'text' }
      },
      {
        id: '4',
        label: 'Deep Learning',
        type: 'concept',
        metadata: { importance: 0.8, modality: 'text' }
      },
      {
        id: '5',
        label: 'Computer Vision',
        type: 'concept',
        metadata: { importance: 0.6, modality: 'text' }
      },
      {
        id: '6',
        label: 'Natural Language Processing',
        type: 'concept',
        metadata: { importance: 0.7, modality: 'text' }
      }
    ],
    edges: [
      { id: 'e1', source: '1', target: '2', type: 'contains', metadata: {} },
      { id: 'e2', source: '2', target: '3', type: 'includes', metadata: {} },
      { id: 'e3', source: '2', target: '4', type: 'includes', metadata: {} },
      { id: 'e4', source: '4', target: '3', type: 'uses', metadata: {} },
      { id: 'e4', source: '1', target: '5', type: 'contains', metadata: {} },
      { id: 'e5', source: '1', target: '6', type: 'contains', metadata: {} }
    ]
  };

  const fetchGraphData = useCallback(async () => {
    if (!searchQuery.trim()) {
      setGraphData(mockGraphData);
      return;
    }

    setIsLoading(true);
    try {
      const data = await api.graphSearch({
        entity: searchQuery,
        tenant_id: tenantId,
        user_id: userId,
      });
      setGraphData(data);
    } catch (error) {
      console.error('Failed to fetch graph data:', error);
      toast.error('Failed to load graph data');
      setGraphData(mockGraphData);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, tenantId, userId]);

  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  const drawGraph = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !graphData) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Simple force-directed layout simulation
    const nodes = graphData.nodes.map(node => ({
      ...node,
      x: Math.random() * (canvas.width - 100) + 50,
      y: Math.random() * (canvas.height - 100) + 50,
      vx: 0,
      vy: 0
    }));

    const edges = graphData.edges;

    // Draw edges first
    ctx.strokeStyle = '#64748b';
    ctx.lineWidth = 1;
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode) {
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);
        ctx.stroke();
      }
    });

    // Draw nodes
    nodes.forEach(node => {
      const isSelected = selectedNode?.id === node.id;
      const isHovered = tooltip?.node.id === node.id;
      
      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, isSelected ? 12 : 8, 0, 2 * Math.PI);
      ctx.fillStyle = isSelected ? '#3b82f6' : isHovered ? '#60a5fa' : '#94a3b8';
      ctx.fill();
      
      // Node border
      ctx.strokeStyle = isSelected ? '#1d4ed8' : '#64748b';
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.stroke();

      // Node label
      if (showLabels) {
        ctx.fillStyle = '#1f2937';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + 25);
      }
    });
  }, [graphData, selectedNode, tooltip, showLabels]);

  useEffect(() => {
    drawGraph();
  }, [drawGraph]);

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !graphData) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Find clicked node
    const clickedNode = graphData.nodes.find(node => {
      // This is a simplified collision detection
      // In a real implementation, you'd store node positions
      return false; // Placeholder
    });

    setSelectedNode(clickedNode || null);
    setTooltip(null);
  };

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !graphData) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Find hovered node
    const hoveredNode = graphData.nodes.find(node => {
      // This is a simplified collision detection
      return false; // Placeholder
    });

    if (hoveredNode) {
      setTooltip({ x: event.clientX, y: event.clientY, node: hoveredNode });
    } else {
      setTooltip(null);
    }
  };

  const resetView = () => {
    drawGraph();
  };

  const zoomIn = () => {
    // Zoom in implementation
  };

  const zoomOut = () => {
    // Zoom out implementation
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Controls */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search entities..."
              className="w-64"
            />
            <Button
              onClick={fetchGraphData}
              disabled={isLoading}
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Search'
              )}
            </Button>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm text-muted-foreground">Radius:</label>
            <Input
              type="number"
              min="1"
              max="5"
              value={radius}
              onChange={(e) => setRadius(parseInt(e.target.value))}
              className="w-16"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowLabels(!showLabels)}
          >
            {showLabels ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          </Button>
          
          <Button variant="outline" size="sm" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          
          <Button variant="outline" size="sm" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          
          <Button variant="outline" size="sm" onClick={resetView}>
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="flex-1 relative">
        <canvas
          ref={canvasRef}
          className="w-full h-full cursor-pointer"
          onClick={handleCanvasClick}
          onMouseMove={handleCanvasMouseMove}
        />
        
        {/* Tooltip */}
        {tooltip && (
          <div
            className="absolute bg-popover border rounded-lg shadow-lg p-3 z-10 pointer-events-none"
            style={{
              left: tooltip.x + 10,
              top: tooltip.y - 10,
            }}
          >
            <div className="space-y-1">
              <h4 className="font-medium">{tooltip.node.label}</h4>
              <Badge variant="outline" className="text-xs">
                {tooltip.node.type}
              </Badge>
              {tooltip.node.metadata?.importance && (
                <p className="text-xs text-muted-foreground">
                  Importance: {(tooltip.node.metadata.importance * 100).toFixed(0)}%
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="border-t p-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Network className="h-5 w-5" />
                <span>{selectedNode.label}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium">Type</h4>
                  <Badge variant="outline">{selectedNode.type}</Badge>
                </div>
                
                {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
                  <div>
                    <h4 className="font-medium">Metadata</h4>
                    <div className="bg-muted p-2 rounded text-sm">
                      <pre>{JSON.stringify(selectedNode.metadata, null, 2)}</pre>
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    View Memory
                  </Button>
                  <Button size="sm" variant="outline">
                    Expand Graph
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Graph Stats */}
      {graphData && (
        <div className="border-t p-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>{graphData.nodes.length} nodes</span>
            <span>{graphData.edges.length} edges</span>
            <span>Radius: {radius}</span>
          </div>
        </div>
      )}
    </div>
  );
}
