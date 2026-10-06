import json
import os
import pytest
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import PhotoRecord

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LIBRARY_PATH = os.path.join(DATA_DIR, "benchmark_library.json")
SCENARIOS_PATH = os.path.join(DATA_DIR, "test_scenarios.json")

def test_library_exists():
    assert os.path.exists(LIBRARY_PATH)
    assert os.path.exists(SCENARIOS_PATH)

def test_library_schema():
    with open(LIBRARY_PATH, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1000
    
    # Validate all records
    for record in data:
        parsed = PhotoRecord(**record)
        assert parsed.photo_id == record['photo_id']

def test_scenarios_exist_in_library():
    with open(LIBRARY_PATH, 'r') as f:
        lib_data = json.load(f)
        
    with open(SCENARIOS_PATH, 'r') as f:
        scenarios = json.load(f)
        
    lib_ids = {r['photo_id'] for r in lib_data}
    
    for s in scenarios:
        assert s['target_photo_id'] in lib_ids, f"Target {s['target_photo_id']} not found in library"
