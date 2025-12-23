"""
Unit tests for KnowledgeExpansionLayer
"""
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from src.profession.knowledge_expansion import KnowledgeExpansionLayer
from src.profession.schema import ProfessionSchema

@pytest.fixture
def dummy_schema():
    # Minimal ProfessionSchema with required fields
    from src.profession.schema import RoleDefinition, ToolsEquipment, DailyTasks, DecisionPatterns, SafetyRules, KnowledgeConfidence, Terminology, EdgeCases
    return ProfessionSchema(
        profession_id="SE-001",
        profession_name="Software Engineer",
        industry="Technology",
        role_definition=RoleDefinition(
            primary_responsibilities=[],
            secondary_responsibilities=[],
            success_metrics=[],
            common_challenges=[]
        ),
        tools_equipment=ToolsEquipment(software=[], hardware=[], platforms=[], methodologies=[], certifications=[]),
        daily_tasks=DailyTasks(routine=[], periodic={}, situational=[]),
        decision_patterns=DecisionPatterns(common_decisions=[], decision_frameworks=[], risk_tolerance=None, information_sources=[], escalation_criteria=[]),
        safety_rules=SafetyRules(critical=[], important=[], best_practices=[], emergency_protocols=[]),
        knowledge_confidence=KnowledgeConfidence(needs_expansion=["primary_responsibilities"], medium_confidence_areas=[], high_confidence_areas=[]),
        terminology=Terminology(jargon={}, acronyms={}, concepts={}),
        edge_cases=EdgeCases(scenarios=[], exceptions=[], escalation_triggers=[]),
        data_sources=[],
        expansion_history=[],
        last_updated=None
    )

@pytest.fixture
def mock_web_agent():
    # Mock LLM provider and web agent
    mock_llm = MagicMock()
    mock_llm.generate.return_value = '{"key_points": ["Writes code"], "facts": ["Uses Python"], "best_practices": ["Write tests"], "sources": ["example.com"], "confidence": "high"}'
    return mock_llm

@pytest.fixture
def knowledge_expander(mock_web_agent):
    # Use dummy API keys and cache dir
    return KnowledgeExpansionLayer(
        llm_provider=mock_web_agent,
        google_api_key="dummy",
        google_cse_id="dummy",
        cache_dir=Path("/tmp/test_cache")
    )

def test_detect_missing_fields(dummy_schema, knowledge_expander):
    # Should detect missing/incomplete fields
    missing = knowledge_expander._detect_query_gaps(dummy_schema, "What are the main responsibilities?")
    assert isinstance(missing, list)


def test_expand_schema_calls_web_agent(dummy_schema, knowledge_expander, mock_web_agent):
    # Patch _web_search to simulate web agent
    knowledge_expander._web_search = MagicMock(return_value=[{"title": "Result", "link": "example.com", "snippet": "Writes code", "displayLink": "example.com"}])
    knowledge_expander._clean_search_results = MagicMock(return_value={
        "key_points": ["Writes code"],
        "facts": ["Uses Python"],
        "best_practices": ["Write tests"],
        "sources": ["example.com"],
        "confidence": "high"
    })
    # Mark area as needing expansion
    dummy_schema.knowledge_confidence.needs_expansion = ["primary_responsibilities"]
    updated = knowledge_expander.expand_schema(dummy_schema)
    assert "Writes code" in str(updated)


def test_merge_expansion(dummy_schema, knowledge_expander):
    # Test merging new data into schema
    area = "primary_responsibilities"
    data = {
        "key_points": ["Writes code", "Reviews code"],
        "facts": ["Uses Python"],
        "best_practices": ["Write tests"],
        "sources": ["example.com"],
        "confidence": "high"
    }
    merged = knowledge_expander._merge_expansion(dummy_schema, area, data)
    assert hasattr(merged, "role_definition")
    assert "Writes code" in str(merged)


def test_expand_schema_no_gaps(dummy_schema, knowledge_expander):
    # If no gaps, schema should be unchanged
    dummy_schema.knowledge_confidence.needs_expansion = []
    result = knowledge_expander.expand_schema(dummy_schema)
    assert result == dummy_schema


def test_merge_conflict_and_trace(dummy_schema, knowledge_expander):
    # Add an existing responsibility and a conflicting one
    dummy_schema.role_definition.primary_responsibilities = ["NEVER deploy without review"]
    area = "primary_responsibilities"
    data = {
        "key_points": ["NEVER deploy without review", "ALWAYS deploy without review"],
        "facts": [],
        "best_practices": [],
        "sources": ["conflict.com"],
        "confidence": "medium"
    }
    merged = knowledge_expander._merge_expansion(dummy_schema, area, data)
    # Check that the duplicate is skipped and the conflict is logged
    last_trace = merged.expansion_history[-1]
    assert "NEVER deploy without review" in last_trace["skipped"]
    assert "ALWAYS deploy without review" in last_trace["conflicts"]
    assert last_trace["area"] == area
    assert "conflict.com" in last_trace["source"]


def test_merge_partial_and_trace(dummy_schema, knowledge_expander):
    # Add an existing tool and a new one
    dummy_schema.tools_equipment.software = ["Python"]
    area = "software_tools"
    data = {
        "key_points": ["Python", "Docker"],
        "facts": [],
        "best_practices": [],
        "sources": ["partial.com"],
        "confidence": "high"
    }
    merged = knowledge_expander._merge_expansion(dummy_schema, area, data)
    last_trace = merged.expansion_history[-1]
    assert "Python" in last_trace["skipped"]
    assert "Docker" in last_trace["added"]
    assert last_trace["area"] == area
    assert "partial.com" in last_trace["source"]


def test_merge_edge_case_trace(dummy_schema, knowledge_expander):
    # Add a new edge case scenario
    area = "edge_cases"
    data = {
        "key_points": ["System outage during deployment"],
        "facts": [],
        "best_practices": [],
        "sources": ["edge.com"],
        "confidence": "medium"
    }
    merged = knowledge_expander._merge_expansion(dummy_schema, area, data)
    last_trace = merged.expansion_history[-1]
    assert "System outage during deployment" in last_trace["added"]
    assert last_trace["area"] == area
    assert "edge.com" in last_trace["source"]
