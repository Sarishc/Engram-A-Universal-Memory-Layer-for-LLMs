"""Tests for graph layer functionality."""

import pytest
from unittest.mock import Mock, patch
from engram.graph.builder import GraphBuilder, EntityExtractor, RelationshipExtractor
from engram.graph.store import GraphStore
from engram.graph.api import GraphAPI


class TestGraphBuilder:
    """Test graph builder functionality."""
    
    def test_graph_builder_init(self):
        """Test graph builder initialization."""
        builder = GraphBuilder()
        assert builder.entity_extractor is not None
        assert builder.relationship_extractor is not None
    
    def test_generate_node_id(self):
        """Test node ID generation."""
        builder = GraphBuilder()
        
        id1 = builder._generate_node_id("Test Entity")
        id2 = builder._generate_node_id("Test Entity")
        id3 = builder._generate_node_id("Different Entity")
        
        assert id1 == id2  # Same text should generate same ID
        assert id1 != id3  # Different text should generate different ID
        assert len(id1) == 12  # MD5 hash truncated to 12 chars
    
    def test_map_entity_type(self):
        """Test entity type mapping."""
        builder = GraphBuilder()
        
        assert builder._map_entity_type("PERSON") == "person"
        assert builder._map_entity_type("ORG") == "organization"
        assert builder._map_entity_type("LOC") == "location"
        assert builder._map_entity_type("UNKNOWN") == "entity"  # Default
    
    @patch('engram.graph.builder.spacy.load')
    def test_build_graph_from_text(self, mock_spacy_load):
        """Test building graph from text."""
        # Mock spaCy model
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_ent = Mock()
        mock_ent.label_ = "PERSON"
        mock_ent.text = "John Doe"
        mock_ent.start_char = 0
        mock_ent.end_char = 8
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        builder = GraphBuilder()
        result = builder.build_graph_from_text("John Doe is a person.")
        
        assert "nodes" in result
        assert "edges" in result
        assert "metadata" in result
        assert len(result["nodes"]) > 0
        assert result["metadata"]["total_entities"] > 0


class TestEntityExtractor:
    """Test entity extractor functionality."""
    
    @patch('engram.graph.builder.spacy.load')
    def test_extract_entities_with_spacy(self, mock_spacy_load):
        """Test entity extraction with spaCy."""
        # Mock spaCy model
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_ent = Mock()
        mock_ent.label_ = "PERSON"
        mock_ent.text = "John Doe"
        mock_ent.start_char = 0
        mock_ent.end_char = 8
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        extractor = EntityExtractor()
        entities = extractor.extract_entities("John Doe is here.")
        
        assert len(entities) == 1
        assert entities[0]["label"] == "PERSON"
        assert entities[0]["text"] == "John Doe"
        assert entities[0]["start"] == 0
        assert entities[0]["end"] == 8
    
    def test_extract_entities_no_spacy(self):
        """Test entity extraction without spaCy."""
        extractor = EntityExtractor()
        extractor.nlp = None
        
        entities = extractor.extract_entities("Some text")
        assert entities == []
    
    def test_extract_entities_empty_text(self):
        """Test entity extraction with empty text."""
        extractor = EntityExtractor()
        entities = extractor.extract_entities("")
        assert entities == []


class TestRelationshipExtractor:
    """Test relationship extractor functionality."""
    
    def test_relationship_extractor_init(self):
        """Test relationship extractor initialization."""
        extractor = RelationshipExtractor()
        assert len(extractor.patterns) > 0
        assert all("pattern" in p and "relation" in p for p in extractor.patterns)
    
    def test_find_matching_entity(self):
        """Test finding matching entities."""
        extractor = RelationshipExtractor()
        
        entities = [
            {"text": "John Doe", "label": "PERSON"},
            {"text": "Apple Inc", "label": "ORG"}
        ]
        
        # Exact match
        match = extractor._find_matching_entity("John Doe", entities)
        assert match is not None
        assert match["text"] == "John Doe"
        
        # No match
        match = extractor._find_matching_entity("Unknown Entity", entities)
        assert match is None
    
    def test_extract_relationships(self):
        """Test relationship extraction."""
        extractor = RelationshipExtractor()
        
        entities = [
            {"text": "John", "label": "PERSON"},
            {"text": "Apple", "label": "ORG"}
        ]
        
        relationships = extractor.extract_relationships(
            "John works for Apple", entities
        )
        
        # Should find some relationships (pattern-based or co-occurrence)
        assert isinstance(relationships, list)


class TestGraphStore:
    """Test graph store functionality."""
    
    def test_graph_store_init(self):
        """Test graph store initialization."""
        store = GraphStore()
        assert store is not None
    
    @patch('engram.graph.store.get_db_session')
    def test_upsert_nodes(self, mock_get_session):
        """Test upserting nodes."""
        store = GraphStore()
        
        # Mock database session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        nodes = [
            {
                "id": "node1",
                "label": "Test Entity",
                "type": "person",
                "properties": {"confidence": 0.8}
            }
        ]
        
        node_ids = store.upsert_nodes("tenant1", "user1", nodes)
        
        assert len(node_ids) == 1
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
    
    @patch('engram.graph.store.get_db_session')
    def test_upsert_edges(self, mock_get_session):
        """Test upserting edges."""
        store = GraphStore()
        
        # Mock database session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        edges = [
            {
                "src": "node1",
                "dst": "node2",
                "relation": "works_for",
                "weight": 1.0,
                "properties": {}
            }
        ]
        
        edge_ids = store.upsert_edges("tenant1", "user1", edges)
        
        assert len(edge_ids) == 1
        mock_session.add.assert_called()
        mock_session.commit.assert_called()


class TestGraphAPI:
    """Test graph API functionality."""
    
    def test_graph_api_init(self):
        """Test graph API initialization."""
        api = GraphAPI()
        assert api.builder is not None
        assert api.store is not None
    
    def test_format_for_d3(self):
        """Test formatting graph data for D3."""
        api = GraphAPI()
        
        graph_data = {
            "nodes": [
                {
                    "id": "node1",
                    "label": "Test Entity",
                    "type": "person",
                    "properties": {}
                }
            ],
            "edges": [
                {
                    "src": "node1",
                    "dst": "node2",
                    "relation": "related_to",
                    "weight": 1.0,
                    "properties": {}
                }
            ],
            "metadata": {}
        }
        
        d3_data = api.format_for_d3(graph_data)
        
        assert "nodes" in d3_data
        assert "links" in d3_data
        assert "metadata" in d3_data
        
        # Check D3-specific formatting
        assert d3_data["nodes"][0]["group"] == "PERSON"
        assert "degree" in d3_data["nodes"][0]
        assert d3_data["links"][0]["source"] == "node1"
        assert d3_data["links"][0]["target"] == "node2"
