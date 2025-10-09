"""Graph storage and persistence layer."""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from engram.utils.logger import get_logger
from engram.utils.ids import generate_ulid
from engram.database.graph_models import Node, Edge
from engram.database.postgres import get_db_session

logger = get_logger(__name__)


class GraphStore:
    """Graph storage and retrieval operations."""
    
    def __init__(self):
        """Initialize graph store."""
        pass
    
    def upsert_nodes(
        self,
        tenant_id: str,
        user_id: str,
        nodes: List[Dict[str, Any]],
        deduplicate: bool = True
    ) -> List[str]:
        """Upsert nodes into the graph store.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            nodes: List of node dictionaries
            deduplicate: Whether to deduplicate nodes by label
            
        Returns:
            List of node IDs that were created/updated
        """
        if not nodes:
            return []
        
        node_ids = []
        
        with get_db_session() as session:
            try:
                for node_data in nodes:
                    node_id = self._upsert_single_node(
                        session, tenant_id, user_id, node_data, deduplicate
                    )
                    node_ids.append(node_id)
                
                session.commit()
                logger.info(f"Upserted {len(node_ids)} nodes for tenant {tenant_id}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error upserting nodes: {e}")
                raise
        
        return node_ids
    
    def _upsert_single_node(
        self,
        session: Session,
        tenant_id: str,
        user_id: str,
        node_data: Dict[str, Any],
        deduplicate: bool
    ) -> str:
        """Upsert a single node.
        
        Args:
            session: Database session
            tenant_id: Tenant identifier
            user_id: User identifier
            node_data: Node data dictionary
            deduplicate: Whether to deduplicate by label
            
        Returns:
            Node ID
        """
        label = node_data["label"]
        node_type = node_data.get("type", "entity")
        properties = node_data.get("properties", {})
        
        if deduplicate:
            # Try to find existing node
            existing_node = session.query(Node).filter(
                Node.tenant_id == tenant_id,
                Node.user_id == user_id,
                Node.label == label,
                Node.node_type == node_type
            ).first()
            
            if existing_node:
                # Update existing node properties
                existing_properties = existing_node.properties or {}
                existing_properties.update(properties)
                existing_node.properties = existing_properties
                return existing_node.id
        
        # Create new node
        node_id = generate_ulid()
        node = Node(
            id=node_id,
            tenant_id=tenant_id,
            user_id=user_id,
            label=label,
            node_type=node_type,
            properties=properties,
        )
        
        session.add(node)
        return node_id
    
    def upsert_edges(
        self,
        tenant_id: str,
        user_id: str,
        edges: List[Dict[str, Any]],
        deduplicate: bool = True
    ) -> List[str]:
        """Upsert edges into the graph store.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            edges: List of edge dictionaries
            deduplicate: Whether to deduplicate edges
            
        Returns:
            List of edge IDs that were created/updated
        """
        if not edges:
            return []
        
        edge_ids = []
        
        with get_db_session() as session:
            try:
                for edge_data in edges:
                    edge_id = self._upsert_single_edge(
                        session, tenant_id, user_id, edge_data, deduplicate
                    )
                    edge_ids.append(edge_id)
                
                session.commit()
                logger.info(f"Upserted {len(edge_ids)} edges for tenant {tenant_id}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error upserting edges: {e}")
                raise
        
        return edge_ids
    
    def _upsert_single_edge(
        self,
        session: Session,
        tenant_id: str,
        user_id: str,
        edge_data: Dict[str, Any],
        deduplicate: bool
    ) -> str:
        """Upsert a single edge.
        
        Args:
            session: Database session
            tenant_id: Tenant identifier
            user_id: User identifier
            edge_data: Edge data dictionary
            deduplicate: Whether to deduplicate edges
            
        Returns:
            Edge ID
        """
        src_id = edge_data["src"]
        dst_id = edge_data["dst"]
        relation = edge_data["relation"]
        weight = edge_data.get("weight", 1.0)
        properties = edge_data.get("properties", {})
        
        if deduplicate:
            # Try to find existing edge
            existing_edge = session.query(Edge).filter(
                Edge.tenant_id == tenant_id,
                Edge.user_id == user_id,
                Edge.src_id == src_id,
                Edge.dst_id == dst_id,
                Edge.relation == relation
            ).first()
            
            if existing_edge:
                # Update existing edge weight (additive)
                existing_edge.weight += weight
                
                # Update properties
                existing_properties = existing_edge.properties or {}
                existing_properties.update(properties)
                existing_edge.properties = existing_properties
                
                return existing_edge.id
        
        # Create new edge
        edge_id = generate_ulid()
        edge = Edge(
            id=edge_id,
            tenant_id=tenant_id,
            user_id=user_id,
            src_id=src_id,
            dst_id=dst_id,
            relation=relation,
            weight=weight,
            properties=properties,
        )
        
        session.add(edge)
        return edge_id
    
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
            Dictionary containing nodes and edges
        """
        with get_db_session() as session:
            try:
                if seed_labels:
                    # Start from specific seed nodes
                    seed_nodes = session.query(Node).filter(
                        Node.tenant_id == tenant_id,
                        Node.user_id == user_id,
                        Node.label.in_(seed_labels)
                    ).all()
                else:
                    # Get random nodes if no seeds provided
                    seed_nodes = session.query(Node).filter(
                        Node.tenant_id == tenant_id,
                        Node.user_id == user_id
                    ).limit(10).all()
                
                if not seed_nodes:
                    return {"nodes": [], "edges": [], "metadata": {"total_nodes": 0, "total_edges": 0}}
                
                # Get nodes and edges within radius
                nodes, edges = self._traverse_graph(
                    session, tenant_id, user_id, seed_nodes, radius, max_nodes
                )
                
                return {
                    "nodes": [node.to_dict() for node in nodes],
                    "edges": [edge.to_dict() for edge in edges],
                    "metadata": {
                        "total_nodes": len(nodes),
                        "total_edges": len(edges),
                        "radius": radius,
                        "seed_labels": seed_labels or [],
                    },
                }
                
            except Exception as e:
                logger.error(f"Error getting subgraph: {e}")
                return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}
    
    def _traverse_graph(
        self,
        session: Session,
        tenant_id: str,
        user_id: str,
        seed_nodes: List[Node],
        radius: int,
        max_nodes: int
    ) -> Tuple[List[Node], List[Edge]]:
        """Traverse graph from seed nodes.
        
        Args:
            session: Database session
            tenant_id: Tenant identifier
            user_id: User identifier
            seed_nodes: List of seed nodes
            radius: Traversal radius
            max_nodes: Maximum nodes to return
            
        Returns:
            Tuple of (nodes, edges)
        """
        visited_nodes = set()
        all_nodes = []
        all_edges = []
        
        current_level = [node.id for node in seed_nodes]
        all_nodes.extend(seed_nodes)
        visited_nodes.update(current_level)
        
        for level in range(radius):
            if not current_level or len(all_nodes) >= max_nodes:
                break
            
            next_level = set()
            
            # Get edges from current level
            edges = session.query(Edge).filter(
                Edge.tenant_id == tenant_id,
                Edge.user_id == user_id,
                Edge.src_id.in_(current_level)
            ).all()
            
            # Add edges to result
            all_edges.extend(edges)
            
            # Get destination nodes
            dst_ids = [edge.dst_id for edge in edges]
            if dst_ids:
                dst_nodes = session.query(Node).filter(
                    Node.tenant_id == tenant_id,
                    Node.user_id == user_id,
                    Node.id.in_(dst_ids)
                ).all()
                
                for node in dst_nodes:
                    if node.id not in visited_nodes and len(all_nodes) < max_nodes:
                        all_nodes.append(node)
                        visited_nodes.add(node.id)
                        next_level.add(node.id)
            
            current_level = list(next_level)
        
        return all_nodes, all_edges
    
    def search_entities(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for entities matching a query.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            query: Search query
            entity_type: Optional entity type filter
            limit: Maximum results to return
            
        Returns:
            List of matching entities
        """
        with get_db_session() as session:
            try:
                query_obj = session.query(Node).filter(
                    Node.tenant_id == tenant_id,
                    Node.user_id == user_id,
                    Node.label.ilike(f"%{query}%")
                )
                
                if entity_type:
                    query_obj = query_obj.filter(Node.node_type == entity_type)
                
                nodes = query_obj.limit(limit).all()
                
                return [node.to_dict() for node in nodes]
                
            except Exception as e:
                logger.error(f"Error searching entities: {e}")
                return []
    
    def get_node_stats(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Get statistics about the graph.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            Dictionary with graph statistics
        """
        with get_db_session() as session:
            try:
                node_count = session.query(Node).filter(
                    Node.tenant_id == tenant_id,
                    Node.user_id == user_id
                ).count()
                
                edge_count = session.query(Edge).filter(
                    Edge.tenant_id == tenant_id,
                    Edge.user_id == user_id
                ).count()
                
                # Get node type distribution
                from sqlalchemy import func
                type_counts = session.query(
                    Node.node_type, func.count(Node.id)
                ).filter(
                    Node.tenant_id == tenant_id,
                    Node.user_id == user_id
                ).group_by(Node.node_type).all()
                
                return {
                    "total_nodes": node_count,
                    "total_edges": edge_count,
                    "node_types": dict(type_counts),
                }
                
            except Exception as e:
                logger.error(f"Error getting node stats: {e}")
                return {"total_nodes": 0, "total_edges": 0, "node_types": {}}
