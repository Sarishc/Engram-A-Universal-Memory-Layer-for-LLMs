"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import * as d3 from "d3"

interface Node {
  id: string
  label: string
  group: string
  importance: number
  type: string
}

interface Link {
  source: string
  target: string
  strength: number
}

interface GraphData {
  nodes: Node[]
  links: Link[]
}

interface GraphViewProps {
  data: GraphData | undefined
  onNodeClick: (node: Node) => void
  settings: {
    showLabels: boolean
    showConnections: boolean
    nodeSize: number
    linkStrength: number
  }
}

export function GraphView({ data, onNodeClick, settings }: GraphViewProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect()
        setDimensions({ width: rect.width, height: rect.height })
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  useEffect(() => {
    if (!data || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const { width, height } = dimensions
    const centerX = width / 2
    const centerY = height / 2

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id((d: any) => d.id).strength(settings.linkStrength))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(centerX, centerY))
      .force("collision", d3.forceCollide().radius(30))

    // Create container for zoom/pan
    const container = svg.append("g")

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        container.attr("transform", event.transform)
      })

    svg.call(zoom)

    // Create links
    const link = container.append("g")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke", "#94a3b8")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d: any) => Math.sqrt(d.strength) * 2)

    // Create nodes
    const node = container.append("g")
      .selectAll("g")
      .data(data.nodes)
      .enter().append("g")
      .attr("class", "node")
      .style("cursor", "pointer")
      .call(d3.drag<SVGGElement, Node>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))

    // Add circles to nodes
    node.append("circle")
      .attr("r", (d: Node) => Math.sqrt(d.importance) * 15 * settings.nodeSize)
      .attr("fill", (d: Node) => {
        const colors = {
          meeting: "#3b82f6",
          research: "#10b981", 
          feedback: "#f59e0b",
          finance: "#ef4444",
          hr: "#8b5cf6",
          product: "#6366f1",
          technical: "#f97316",
        }
        return colors[d.group as keyof typeof colors] || "#6b7280"
      })
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 2)
      .attr("opacity", 0.8)

    // Add labels
    if (settings.showLabels) {
      node.append("text")
        .text((d: Node) => d.label)
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("font-size", "12px")
        .attr("font-weight", "500")
        .attr("fill", "#1f2937")
        .attr("pointer-events", "none")
    }

    // Add click handlers
    node.on("click", (event, d: Node) => {
      event.stopPropagation()
      onNodeClick(d)
    })

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y)

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`)
    })

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [data, dimensions, settings, onNodeClick])

  return (
    <div className="w-full h-full relative">
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800"
      />
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <h4 className="text-sm font-semibold mb-2">Node Types</h4>
        <div className="space-y-1 text-xs">
          {[
            { group: "meeting", color: "#3b82f6", label: "Meetings" },
            { group: "research", color: "#10b981", label: "Research" },
            { group: "feedback", color: "#f59e0b", label: "Feedback" },
            { group: "finance", color: "#ef4444", label: "Finance" },
            { group: "hr", color: "#8b5cf6", label: "HR" },
            { group: "product", color: "#6366f1", label: "Product" },
            { group: "technical", color: "#f97316", label: "Technical" },
          ].map((item) => (
            <div key={item.group} className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 right-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <div className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
          <div>• Click and drag to pan</div>
          <div>• Scroll to zoom</div>
          <div>• Click nodes for details</div>
        </div>
      </div>
    </div>
  )
}
