import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import ParsedAnchor, TemporalAnchor
from engine.facet_controller import FacetController
from engine.timeline_slicer import TimelineSlicer
from engine.hybrid_pipeline import HybridPipeline
from core.llm_client import LLMClient
from core.config import Config

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LIBRARY_PATH = os.path.join(DATA_DIR, "benchmark_library.json")

def test_ambient_facet_overrides():
    slicer = TimelineSlicer(LIBRARY_PATH)
    llm = LLMClient(api_key="test_dummy")
    pipeline = HybridPipeline(slicer, llm)
    
    # Simulate parsed anchor for Goa March 2025
    anchor = ParsedAnchor(
        has_anchor=True,
        temporal=TemporalAnchor(
            raw_text="March 2025",
            anchor_type="month_year",
            resolved_start_iso="2025-03-01T00:00:00Z",
            resolved_end_iso="2025-03-31T23:59:59Z",
            confidence=0.95
        ),
        location_name="Goa, India",
        media_type="photo",
        soft_visual_clues=["cafe"]
    )
    
    state = FacetController.init_from_anchor(anchor)
    assert len(state.chips) >= 3
    
    # 1. Initial slice: March 2025 in Goa
    res_march = pipeline.process_query("Goa March 2025 cafe", Config.REFERENCE_DATE, state, parsed_anchor=anchor)
    assert res_march.neighborhood_size > 0
    assert any("2025-03" in p.photo.timestamp for p in res_march.photos)
    
    # 2. Tactile dropdown override: switch month to April (month = 4)
    state.active_overrides["month"] = 4
    res_april = pipeline.process_query("Goa March 2025 cafe", Config.REFERENCE_DATE, state, parsed_anchor=anchor)
    assert res_april.neighborhood_size > 0
    assert all("2025-04" in p.photo.timestamp for p in res_april.photos)
    
    # 3. Tactile dropdown override: switch year to 2024
    state.active_overrides["year"] = 2024
    state.active_overrides["month"] = 7
    state.active_overrides["location_name"] = "London, UK"
    res_london = pipeline.process_query("Goa March 2025 cafe", Config.REFERENCE_DATE, state, parsed_anchor=anchor)
    assert res_london.neighborhood_size > 0
    assert any("2024-07" in p.photo.timestamp for p in res_london.photos)
    assert any("London" in p.photo.location_name for p in res_london.photos)
