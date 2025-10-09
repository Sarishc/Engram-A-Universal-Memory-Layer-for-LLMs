"""Graph builder for extracting entities and relationships from text."""

import re
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter

from engram.utils.logger import get_logger
from engram.utils.config import get_settings
from engram.database.models import ModalityType

logger = get_logger(__name__)
settings = get_settings()


class EntityExtractor:
    """Extract entities from text using spaCy NER."""
    
    def __init__(self):
        """Initialize entity extractor."""
        self.nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model for NER."""
        try:
            import spacy
            model_name = getattr(settings, 'spacy_model', 'en_core_web_sm')
            return spacy.load(model_name)
        except OSError:
            logger.warning(f"spaCy model not found. Install with: python -m spacy download {model_name}")
            return None
        except ImportError:
            logger.warning("spaCy not available. Install with: pip install spacy")
            return None
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of entity dictionaries with label, text, start, end
        """
        if not self.nlp or not text.strip():
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "label": ent.label_,
                    "text": ent.text.strip(),
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 1.0,  # spaCy doesn't provide confidence scores
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []


class RelationshipExtractor:
    """Extract relationships between entities."""
    
    def __init__(self):
        """Initialize relationship extractor."""
        self.patterns = self._load_relationship_patterns()
    
    def _load_relationship_patterns(self) -> List[Dict[str, Any]]:
        """Load relationship extraction patterns.
        
        Returns:
            List of pattern dictionaries
        """
        return [
            # Person relationships
            {"pattern": r"(\w+)\s+(?:is|was)\s+(?:a|an|the)\s+(\w+)", "relation": "is_a"},
            {"pattern": r"(\w+)\s+(?:works|worked)\s+(?:for|at|in)\s+(\w+)", "relation": "works_for"},
            {"pattern": r"(\w+)\s+(?:lives|lived)\s+(?:in|at)\s+(\w+)", "relation": "lives_in"},
            {"pattern": r"(\w+)\s+(?:born|was born)\s+(?:in|at)\s+(\w+)", "relation": "born_in"},
            
            # Organization relationships
            {"pattern": r"(\w+)\s+(?:founded|founded by)\s+(\w+)", "relation": "founded_by"},
            {"pattern": r"(\w+)\s+(?:acquired|acquired by)\s+(\w+)", "relation": "acquired_by"},
            {"pattern": r"(\w+)\s+(?:partners|partnership)\s+(?:with|and)\s+(\w+)", "relation": "partners_with"},
            
            # Technology relationships
            {"pattern": r"(\w+)\s+(?:uses|used by)\s+(\w+)", "relation": "uses"},
            {"pattern": r"(\w+)\s+(?:built|built with)\s+(\w+)", "relation": "built_with"},
            {"pattern": r"(\w+)\s+(?:compatible|compatible with)\s+(\w+)", "relation": "compatible_with"},
            
            # General relationships
            {"pattern": r"(\w+)\s+(?:causes|caused by)\s+(\w+)", "relation": "causes"},
            {"pattern": r"(\w+)\s+(?:contains|contained in)\s+(\w+)", "relation": "contains"},
            {"pattern": r"(\w+)\s+(?:depends|depends on)\s+(\w+)", "relation": "depends_on"},
        ]
    
    def extract_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships from text.
        
        Args:
            text: Text to extract relationships from
            entities: List of extracted entities
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        # Extract using patterns
        for pattern_info in self.patterns:
            pattern = pattern_info["pattern"]
            relation_type = pattern_info["relation"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                head = match.group(1).strip()
                tail = match.group(2).strip()
                
                # Check if head and tail are entities
                head_entity = self._find_matching_entity(head, entities)
                tail_entity = self._find_matching_entity(tail, entities)
                
                if head_entity and tail_entity:
                    relationships.append({
                        "head": head_entity["text"],
                        "tail": tail_entity["text"],
                        "relation": relation_type,
                        "confidence": 0.8,  # Pattern-based confidence
                        "head_type": head_entity["label"],
                        "tail_type": tail_entity["label"],
                    })
        
        # Extract co-occurrence relationships
        co_occurrence_rels = self._extract_co_occurrence_relationships(entities)
        relationships.extend(co_occurrence_rels)
        
        return relationships
    
    def _find_matching_entity(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find entity that matches the given text.
        
        Args:
            text: Text to match
            entities: List of entities
            
        Returns:
            Matching entity or None
        """
        text_lower = text.lower()
        
        for entity in entities:
            if entity["text"].lower() == text_lower:
                return entity
            
            # Check for partial matches
            if text_lower in entity["text"].lower() or entity["text"].lower() in text_lower:
                return entity
        
        return None
    
    def _extract_co_occurrence_relationships(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract co-occurrence relationships between entities.
        
        Args:
            entities: List of entities
            
        Returns:
            List of co-occurrence relationships
        """
        relationships = []
        
        # Group entities by proximity (within 50 characters)
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Check if entities are close to each other
                if abs(entity1["start"] - entity2["start"]) < 50:
                    relationships.append({
                        "head": entity1["text"],
                        "tail": entity2["text"],
                        "relation": "co_occurs_with",
                        "confidence": 0.3,  # Lower confidence for co-occurrence
                        "head_type": entity1["label"],
                        "tail_type": entity2["label"],
                    })
        
        return relationships


class GraphBuilder:
    """Build knowledge graph from text content."""
    
    def __init__(self):
        """Initialize graph builder."""
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
    
    def build_graph_from_text(self, text: str, modality: ModalityType = ModalityType.TEXT) -> Dict[str, Any]:
        """Build graph from text content.
        
        Args:
            text: Text content to process
            modality: Content modality type
            
        Returns:
            Dictionary containing nodes and edges
        """
        try:
            logger.info(f"Building graph from {modality.value} content")
            
            # Extract entities
            entities = self.entity_extractor.extract_entities(text)
            
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(text, entities)
            
            # Create nodes from entities
            nodes = []
            node_map = {}  # Map entity text to node ID
            
            for entity in entities:
                # Normalize entity text
                normalized_text = entity["text"].strip()
                if normalized_text in node_map:
                    continue  # Skip duplicates
                
                node_id = self._generate_node_id(normalized_text)
                node_map[normalized_text] = node_id
                
                nodes.append({
                    "id": node_id,
                    "label": normalized_text,
                    "type": self._map_entity_type(entity["label"]),
                    "properties": {
                        "original_type": entity["label"],
                        "confidence": entity["confidence"],
                        "modality": modality.value,
                    },
                })
            
            # Create edges from relationships
            edges = []
            for rel in relationships:
                head_id = node_map.get(rel["head"])
                tail_id = node_map.get(rel["tail"])
                
                if head_id and tail_id:
                    edges.append({
                        "src": head_id,
                        "dst": tail_id,
                        "relation": rel["relation"],
                        "weight": rel["confidence"],
                        "properties": {
                            "head_type": rel["head_type"],
                            "tail_type": rel["tail_type"],
                            "modality": modality.value,
                        },
                    })
            
            logger.info(f"Built graph with {len(nodes)} nodes and {len(edges)} edges")
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_entities": len(entities),
                    "total_relationships": len(relationships),
                    "modality": modality.value,
                },
            }
            
        except Exception as e:
            logger.error(f"Error building graph from text: {e}")
            return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}
    
    def _generate_node_id(self, text: str) -> str:
        """Generate a unique node ID from text.
        
        Args:
            text: Entity text
            
        Returns:
            Unique node ID
        """
        # Simple hash-based ID generation
        import hashlib
        return hashlib.md5(text.lower().encode()).hexdigest()[:12]
    
    def _map_entity_type(self, spacy_label: str) -> str:
        """Map spaCy entity labels to our node types.
        
        Args:
            spacy_label: spaCy entity label
            
        Returns:
            Mapped node type
        """
        mapping = {
            "PERSON": "person",
            "ORG": "organization", 
            "GPE": "location",  # Geopolitical entity
            "LOC": "location",
            "FAC": "facility",
            "PRODUCT": "product",
            "EVENT": "event",
            "WORK_OF_ART": "work",
            "LAW": "law",
            "LANGUAGE": "language",
            "DATE": "date",
            "TIME": "time",
            "MONEY": "money",
            "PERCENT": "percentage",
            "QUANTITY": "quantity",
            "ORDINAL": "ordinal",
            "CARDINAL": "cardinal",
        }
        
        return mapping.get(spacy_label, "entity")
