"""Graph API endpoints and utilities."""

from typing import List, Dict, Any, Optional

from engram.utils.logger import get_logger
from engram.graph.builder import GraphBuilder
from engram.graph.store import GraphStore

logger = get_logger(__name__)


class GraphAPI:
    """API layer for graph operations."""
    
    def __init__(self):
        """Initialize graph API."""
        self.builder = GraphBuilder()
        self.store = GraphStore()
    
    def process_text_and_store(
        self,
        tenant_id: str,
        user_id: str,
        text: str,
        modality: str = "text"
    ) -> Dict[str, Any]:
        """Process text and store resulting graph.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            text: Text to process
            modality: Content modality
            
        Returns:
            Dictionary with processing results
        """
        try:
            from engram.database.models import ModalityType
            
            # Build graph from text
            graph_data = self.builder.build_graph_from_text(text, ModalityType(modality))
            
            if not graph_data["nodes"]:
                return {
                    "status": "success",
                    "nodes_created": 0,
                    "edges_created": 0,
                    "message": "No entities found in text"
                }
            
            # Store nodes and edges
            node_ids = self.store.upsert_nodes(tenant_id, user_id, graph_data["nodes"])
            edge_ids = self.store.upsert_edges(tenant_id, user_id, graph_data["edges"])
            
            return {
                "status": "success",
                "nodes_created": len(node_ids),
                "edges_created": len(edge_ids),
                "graph_data": graph_data,
            }
            
        except Exception as e:
            logger.error(f"Error processing text and storing graph: {e}")
            return {
                "status": "error",
                "error": str(e),
                "nodes_created": 0,
                "edges_created": 0,
            }
    
    def get_subgraph(
        self,
        tenant_id: str,
        user_id: str,
        seed_labels: Optional[List[str]] = None,
        radius: int = 2,
        max_nodes: int = 100
    ) -> Dict[str, Any]:
        """Get a subgraph around seed nodes.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            seed_labels: List of seed node labels
            radius: Graph traversal radius
            max_nodes: Maximum number of nodes to return
            
        Returns:
            Dictionary containing subgraph data
        """
        return self.store.get_subgraph(
            tenant_id=tenant_id,
            user_id=user_id,
            seed_labels=seed_labels,
            radius=radius,
            max_nodes=max_nodes
        )
    
    def search_entities(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for entities matching a query.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Search query
            entity_type: Optional entity type filter
            limit: Maximum results to return
            
        Returns:
            Dictionary with search results
        """
        entities = self.store.search_entities(
            tenant_id=tenant_id,
            user_id=user_id,
            query=query,
            entity_type=entity_type,
            limit=limit
        )
        
        return {
            "entities": entities,
            "total": len(entities),
            "query": query,
            "entity_type": entity_type,
        }
    
    def get_graph_stats(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Get graph statistics.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            Dictionary with graph statistics
        """
        return self.store.get_node_stats(tenant_id, user_id)
    
    def format_for_d3(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format graph data for D3.js visualization.
        
        Args:
            graph_data: Graph data from store
            
        Returns:
            D3-formatted graph data
        """
        nodes = []
        links = []
        
        # Format nodes for D3
        for node in graph_data.get("nodes", []):
            # Calculate degree (number of connections)
            degree = sum(1 for edge in graph_data.get("edges", [])
                        if edge["src"] == node["id"] or edge["dst"] == node["id"])
            
            nodes.append({
                "id": node["id"],
                "label": node["label"],
                "type": node["type"],
                "group": node.get("properties", {}).get("original_type", "entity"),
                "degree": degree,
                "properties": node.get("properties", {}),
            })
        
        # Format edges for D3
        for edge in graph_data.get("edges", []):
            links.append({
                "source": edge["src"],
                "target": edge["dst"],
                "relation": edge["relation"],
                "weight": edge["weight"],
                "properties": edge.get("properties", {}),
            })
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": graph_data.get("metadata", {}),
        }
