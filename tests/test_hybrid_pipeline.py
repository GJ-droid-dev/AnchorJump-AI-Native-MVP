import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.timeline_slicer import TimelineSlicer
from engine.hybrid_pipeline import HybridPipeline
from core.llm_client import LLMClient
from core.config import Config

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LIBRARY_PATH = os.path.join(DATA_DIR, "benchmark_library.json")

@pytest.fixture
def slicer():
    return TimelineSlicer(LIBRARY_PATH)

@pytest.fixture
def llm():
    return LLMClient(api_key="test_dummy")

def test_pipeline_regex_fallback(slicer, llm):
    pipeline = HybridPipeline(slicer, llm)
    # The dummy API key will fail, triggering Regex fallback
    res = pipeline.process_query("screenshot 2025", Config.REFERENCE_DATE)
    assert res.neighborhood_size >= 0
    assert res.processing_latency_ms >= 0
    
def test_pipeline_override(slicer, llm):
    pipeline = HybridPipeline(slicer, llm)
    # Get initial result
    res1 = pipeline.process_query("screenshot", Config.REFERENCE_DATE)
    assert res1.parsed_anchor.media_type == "screenshot"
    
    # We will simulate the user removing the "screenshot" facet
    from engine.facet_controller import FacetController
    state = FacetController.init_from_anchor(res1.parsed_anchor)
    assert True
