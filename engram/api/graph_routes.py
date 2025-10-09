"""Graph API routes for knowledge graph operations."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

from engram.utils.logger import get_logger
from engram.graph.api import GraphAPI

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/graph", tags=["graph"])

# Initialize graph API
graph_api = GraphAPI()


class SubgraphRequest(BaseModel):
    """Request model for subgraph retrieval."""
    tenant_id: str = Field(..., description="Tenant identifier")
    user_id: str = Field(..., description="User identifier")
    seed_labels: Optional[List[str]] = Field(default=None, description="Seed node labels")
    radius: int = Field(default=2, description="Graph traversal radius")
    max_nodes: int = Field(default=100, description="Maximum nodes to return")


class SubgraphResponse(BaseModel):
    """Response model for subgraph retrieval."""
    nodes: List[dict] = Field(..., description="List of nodes")
    edges: List[dict] = Field(..., description="List of edges")
    metadata: dict = Field(..., description="Graph metadata")


class EntitySearchRequest(BaseModel):
    """Request model for entity search."""
    tenant_id: str = Field(..., description="Tenant identifier")
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Search query")
    entity_type: Optional[str] = Field(default=None, description="Entity type filter")
    limit: int = Field(default=20, description="Maximum results to return")


class EntitySearchResponse(BaseModel):
    """Response model for entity search."""
    entities: List[dict] = Field(..., description="List of matching entities")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Search query")
    entity_type: Optional[str] = Field(default=None, description="Entity type filter")


@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    tenant_id: str = Query(..., description="Tenant identifier"),
    user_id: str = Query(..., description="User identifier"),
    seed_label: Optional[str] = Query(default=None, description="Seed node label"),
    radius: int = Query(default=2, description="Graph traversal radius"),
    max_nodes: int = Query(default=100, description="Maximum nodes to return"),
):
    """Get a subgraph around seed nodes.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier
        seed_label: Single seed node label
        radius: Graph traversal radius
        max_nodes: Maximum number of nodes to return
        
    Returns:
        Subgraph data
    """
    try:
        seed_labels = [seed_label] if seed_label else None
        
        result = graph_api.get_subgraph(
            tenant_id=tenant_id,
            user_id=user_id,
            seed_labels=seed_labels,
            radius=radius,
            max_nodes=max_nodes
        )
        
        return SubgraphResponse(
            nodes=result.get("nodes", []),
            edges=result.get("edges", []),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error getting subgraph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=EntitySearchResponse)
async def search_entities(
    tenant_id: str = Query(..., description="Tenant identifier"),
    user_id: str = Query(..., description="User identifier"),
    entity: str = Query(..., description="Entity search query"),
    entity_type: Optional[str] = Query(default=None, description="Entity type filter"),
    limit: int = Query(default=20, description="Maximum results to return"),
):
    """Search for entities matching a query.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier
        entity: Search query
        entity_type: Optional entity type filter
        limit: Maximum results to return
        
    Returns:
        Search results
    """
    try:
        result = graph_api.search_entities(
            tenant_id=tenant_id,
            user_id=user_id,
            query=entity,
            entity_type=entity_type,
            limit=limit
        )
        
        return EntitySearchResponse(
            entities=result.get("entities", []),
            total=result.get("total", 0),
            query=result.get("query", entity),
            entity_type=result.get("entity_type", entity_type)
        )
        
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_graph_stats(
    tenant_id: str = Query(..., description="Tenant identifier"),
    user_id: str = Query(..., description="User identifier"),
):
    """Get graph statistics.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier
        
    Returns:
        Graph statistics
    """
    try:
        stats = graph_api.get_graph_stats(tenant_id, user_id)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting graph stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subgraph/d3")
async def get_subgraph_d3(
    tenant_id: str = Query(..., description="Tenant identifier"),
    user_id: str = Query(..., description="User identifier"),
    seed_label: Optional[str] = Query(default=None, description="Seed node label"),
    radius: int = Query(default=2, description="Graph traversal radius"),
    max_nodes: int = Query(default=100, description="Maximum nodes to return"),
):
    """Get a subgraph formatted for D3.js visualization.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier
        seed_label: Single seed node label
        radius: Graph traversal radius
        max_nodes: Maximum number of nodes to return
        
    Returns:
        D3-formatted graph data
    """
    try:
        seed_labels = [seed_label] if seed_label else None
        
        result = graph_api.get_subgraph(
            tenant_id=tenant_id,
            user_id=user_id,
            seed_labels=seed_labels,
            radius=radius,
            max_nodes=max_nodes
        )
        
        # Format for D3
        d3_data = graph_api.format_for_d3(result)
        return d3_data
        
    except Exception as e:
        logger.error(f"Error getting D3 subgraph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_class=HTMLResponse)
async def graph_visualization():
    """Serve the graph visualization page.
    
    Returns:
        HTML page with D3.js graph visualization
    """
    try:
        # Read the static HTML file
        import os
        html_path = os.path.join(os.path.dirname(__file__), "..", "static", "graph.html")
        
        if os.path.exists(html_path):
            with open(html_path, "r") as f:
                return HTMLResponse(content=f.read())
        else:
            # Return a simple HTML page if static file doesn't exist
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Engram Graph Visualization</title>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    #graph { border: 1px solid #ccc; margin: 20px 0; }
                    .node { stroke: #fff; stroke-width: 2px; }
                    .link { stroke: #999; stroke-opacity: 0.6; }
                </style>
            </head>
            <body>
                <h1>Engram Knowledge Graph</h1>
                <p>Graph visualization will be displayed here.</p>
                <div id="graph"></div>
                <script>
                    // Simple D3.js graph visualization
                    const width = 800;
                    const height = 600;
                    
                    const svg = d3.select("#graph")
                        .append("svg")
                        .attr("width", width)
                        .attr("height", height);
                    
                    // Add some sample data for demonstration
                    const data = {
                        nodes: [
                            {id: "1", label: "Sample Node 1", type: "entity"},
                            {id: "2", label: "Sample Node 2", type: "entity"}
                        ],
                        links: [
                            {source: "1", target: "2", relation: "related_to"}
                        ]
                    };
                    
                    const simulation = d3.forceSimulation(data.nodes)
                        .force("link", d3.forceLink(data.links).id(d => d.id))
                        .force("charge", d3.forceManyBody().strength(-300))
                        .force("center", d3.forceCenter(width / 2, height / 2));
                    
                    const link = svg.append("g")
                        .selectAll("line")
                        .data(data.links)
                        .enter().append("line")
                        .attr("class", "link");
                    
                    const node = svg.append("g")
                        .selectAll("circle")
                        .data(data.nodes)
                        .enter().append("circle")
                        .attr("class", "node")
                        .attr("r", 10);
                    
                    node.append("title")
                        .text(d => d.label);
                    
                    simulation.on("tick", () => {
                        link
                            .attr("x1", d => d.source.x)
                            .attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x)
                            .attr("y2", d => d.target.y);
                        
                        node
                            .attr("cx", d => d.x)
                            .attr("cy", d => d.y);
                    });
                </script>
            </body>
            </html>
            """)
            
    except Exception as e:
        logger.error(f"Error serving graph visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))
