import re
from datetime import datetime
from typing import Tuple, Optional

def resolve_temporal_bounds(raw_text: str, anchor_type: str, ref_date: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
    if not raw_text:
        return None, None
        
    raw_lower = raw_text.lower()
    
    # 5 years ago
    match = re.search(r'(\d+)\s*years?\s*ago', raw_lower)
    if match:
        years = int(match.group(1))
        target_year = ref_date.year - years
        return datetime(target_year, 1, 1), datetime(target_year, 12, 31, 23, 59, 59)
        
    # last year
    if "last year" in raw_lower:
        target_year = ref_date.year - 1
        return datetime(target_year, 1, 1), datetime(target_year, 12, 31, 23, 59, 59)
        
    # last december
    if "last december" in raw_lower:
        # If we are in Oct 2026, last December is Dec 2025
        target_year = ref_date.year - 1
        return datetime(target_year, 12, 1), datetime(target_year, 12, 31, 23, 59, 59)
        
    # fallback for 2023, 2024, etc if LLM didn't resolve
    year_match = re.search(r'\b(202\d)\b', raw_lower)
    if year_match:
        year = int(year_match.group(1))
        return datetime(year, 1, 1), datetime(year, 12, 31, 23, 59, 59)
        
    return None, None
