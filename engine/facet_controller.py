from typing import List, Dict, Any, Optional
from core.schemas import ParsedAnchor, FacetChip, FacetOverrideState

import calendar
from datetime import datetime

class FacetController:
    @staticmethod
    def init_from_anchor(anchor: ParsedAnchor) -> FacetOverrideState:
        chips = []
        
        if anchor.temporal and anchor.temporal.resolved_start_iso and anchor.temporal.resolved_end_iso:
            start_dt = datetime.fromisoformat(anchor.temporal.resolved_start_iso.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(anchor.temporal.resolved_end_iso.replace('Z', '+00:00'))
            
            # Emit Year Chip
            chips.append(FacetChip(
                chip_id="temporal_year",
                category="year",
                label=str(start_dt.year),
                value=start_dt.year
            ))
            
            # Emit Month Chip if range is <= 31 days (meaning it's roughly a month or exact date)
            if start_dt.month == end_dt.month and (end_dt - start_dt).days <= 31:
                month_name = calendar.month_name[start_dt.month]
                chips.append(FacetChip(
                    chip_id="temporal_month",
                    category="month",
                    label=month_name,
                    value=start_dt.month
                ))
            
        if anchor.media_type and anchor.media_type != "all":
            chips.append(FacetChip(
                chip_id="media_1",
                category="media_type",
                label=anchor.media_type.capitalize(),
                value=anchor.media_type
            ))
            
        if anchor.event_tag:
            chips.append(FacetChip(
                chip_id="event_1",
                category="event",
                label=anchor.event_tag,
                value=anchor.event_tag
            ))
            
        if anchor.location_name:
            chips.append(FacetChip(
                chip_id="loc_1",
                category="location",
                label=anchor.location_name,
                value=anchor.location_name
            ))
            
        return FacetOverrideState(chips=chips, active_overrides={})
        
    @staticmethod
    def compute_active_filters(state: FacetOverrideState) -> Dict[str, Any]:
        filters = {
            "start_iso": None,
            "end_iso": None,
            "year": None,
            "month": None,
            "media_type": "all",
            "event_tag": None,
            "location_name": None
        }
        
        for chip in state.chips:
            if not chip.is_active:
                continue
                
            if chip.category == "year":
                filters["year"] = chip.value
            elif chip.category == "month":
                filters["month"] = chip.value
            elif chip.category == "media_type":
                filters["media_type"] = chip.value
            elif chip.category == "event":
                filters["event_tag"] = chip.value
            elif chip.category == "location":
                filters["location_name"] = chip.value
                
        # Overrides replace chip values if present
        for key, val in state.active_overrides.items():
            if key in filters:
                filters[key] = val
                
        return filters
