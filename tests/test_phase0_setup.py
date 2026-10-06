import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schemas import ParsedAnchor
from core.config import Config
from core.llm_client import LLMClient

def test_schemas_import():
    assert ParsedAnchor is not None

def test_config_loads():
    assert Config.REFERENCE_DATE == "2026-10-06T00:00:00Z"

def test_llm_client_init():
    client = LLMClient(api_key="dummy_test_key")
    assert client.client is not None
