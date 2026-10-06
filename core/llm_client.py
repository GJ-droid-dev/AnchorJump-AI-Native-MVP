import os
import json
import time
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from .config import Config

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or Config.GEMINI_API_KEY
        if not key:
            from .config import _get_gemini_key
            key = _get_gemini_key()
        if not key:
            self.client = None
        else:
            self.client = genai.Client(api_key=key)

    def parse_anchor(self, query: str, reference_date: str) -> Dict[str, Any]:
        """
        Calls Gemini to parse the query into an anchor schema.
        Includes retry logic and timeout.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not set.")
            
        system_instruction = f"You are an AI semantic parser for a photo retrieval system. The current reference date is {reference_date}."
        prompt = f"Parse the following query into the expected JSON structure: '{query}'"
        
        from core.schemas import ParsedAnchor
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0,
                        response_mime_type="application/json",
                        response_schema=ParsedAnchor,
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                if attempt == 2:
                    raise e
                time.sleep(0.5 * (attempt + 1))
