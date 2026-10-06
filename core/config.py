import os
from dotenv import load_dotenv

load_dotenv()

def _get_gemini_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = str(st.secrets["GEMINI_API_KEY"])
        except Exception:
            pass
    return key

class Config:
    GEMINI_API_KEY = _get_gemini_key()
    APP_ENV = os.getenv("APP_ENV", "development")
    REFERENCE_DATE = os.getenv("REFERENCE_DATE", "2026-10-06T00:00:00Z")
    
    # Path settings
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LIBRARY_PATH = os.path.join(DATA_DIR, "benchmark_library.json")
    SCENARIOS_PATH = os.path.join(DATA_DIR, "test_scenarios.json")
