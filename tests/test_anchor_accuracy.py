import pytest
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.anchor_parser import RegexAnchorFallback
from engine.temporal_resolver import resolve_temporal_bounds

def test_regex_fallback_year():
    ref_dt = datetime(2026, 10, 6)
    parsed = RegexAnchorFallback.parse("Goa trip 2023", ref_dt)
    assert parsed.has_anchor
    assert parsed.temporal.anchor_type == "year_only"
    assert parsed.temporal.resolved_start_iso == "2023-01-01T00:00:00Z"
    
def test_regex_fallback_screenshot():
    ref_dt = datetime(2026, 10, 6)
    parsed = RegexAnchorFallback.parse("screenshot 2025", ref_dt)
    assert parsed.media_type == "screenshot"
    
def test_temporal_resolver_relative():
    ref_dt = datetime(2026, 10, 6)
    start_dt, end_dt = resolve_temporal_bounds("last December", "relative_offset", ref_dt)
    assert start_dt == datetime(2025, 12, 1)
    assert end_dt == datetime(2025, 12, 31, 23, 59, 59)
    
    start_dt, end_dt = resolve_temporal_bounds("5 years ago", "relative_offset", ref_dt)
    assert start_dt == datetime(2021, 1, 1)
    assert end_dt == datetime(2021, 12, 31, 23, 59, 59)
