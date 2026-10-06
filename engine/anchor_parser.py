import re
import time
from datetime import datetime
from typing import Dict, Any

from core.llm_client import LLMClient
from core.schemas import ParsedAnchor, TemporalAnchor
from engine.prompts import ANCHOR_PARSER_SYSTEM_PROMPT
from engine.temporal_resolver import resolve_temporal_bounds

class RegexAnchorFallback:
    @staticmethod
    def parse(query: str, ref_date: datetime) -> ParsedAnchor:
        query_lower = query.lower()
        temporal = None
        
        # Simple year extraction
        year_match = re.search(r'\b(202[1-6])\b', query_lower)
        if year_match:
            year = int(year_match.group(1))
            start_iso = f"{year}-01-01T00:00:00Z"
            end_iso = f"{year}-12-31T23:59:59Z"
            temporal = TemporalAnchor(
                raw_text=str(year),
                anchor_type="year_only",
                resolved_start_iso=start_iso,
                resolved_end_iso=end_iso,
                confidence=0.5
            )
            
        media_type = "all"
        if "screenshot" in query_lower: media_type = "screenshot"
        elif "receipt" in query_lower: media_type = "receipt"
            
        return ParsedAnchor(
            has_anchor=temporal is not None,
            temporal=temporal,
            media_type=media_type,
            soft_visual_clues=[w for w in query_lower.split() if len(w) > 3]
        )

class AnchorParser:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    def parse(self, query: str, reference_date_iso: str) -> ParsedAnchor:
        t0 = time.time()
        try:
            raw_dict = self.llm.parse_anchor(query, reference_date_iso)
            parsed = ParsedAnchor(**raw_dict)
            
            # Post-process relative dates
            if parsed.temporal and not parsed.temporal.resolved_start_iso:
                ref_dt = datetime.fromisoformat(reference_date_iso.replace('Z', '+00:00'))
                start_dt, end_dt = resolve_temporal_bounds(parsed.temporal.raw_text, parsed.temporal.anchor_type, ref_dt)
                if start_dt and end_dt:
                    parsed.temporal.resolved_start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    parsed.temporal.resolved_end_iso = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    
        except Exception as e:
            # Fallback
            ref_dt = datetime.fromisoformat(reference_date_iso.replace('Z', '+00:00'))
            parsed = RegexAnchorFallback.parse(query, ref_dt)
            
        parsed.parsing_latency_ms = (time.time() - t0) * 1000
        return parsed
