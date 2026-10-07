import time
from typing import List, Optional
from core.llm_client import LLMClient
from engine.anchor_parser import AnchorParser
from engine.facet_controller import FacetController
from engine.timeline_slicer import TimelineSlicer
from engine.baseline_matcher import BaselineMatcher
from core.schemas import NeighborhoodResult, ParsedAnchor, FacetOverrideState

class HybridPipeline:
    def __init__(self, slicer: TimelineSlicer, llm_client: LLMClient):
        self.slicer = slicer
        self.parser = AnchorParser(llm_client)
        
    def process_query(self, query: str, ref_date_iso: str, 
                      override_state: Optional[FacetOverrideState] = None,
                      parsed_anchor: Optional[ParsedAnchor] = None) -> NeighborhoodResult:
        t0 = time.time()
        
        # 1. Parse Anchor (Only if no manual override state is provided)
        if not override_state:
            anchor = self.parser.parse(query, ref_date_iso)
            facet_state = FacetController.init_from_anchor(anchor)
        else:
            anchor = parsed_anchor or ParsedAnchor(has_anchor=True, media_type="all")
            facet_state = override_state
            
        # 2. Compute Active Filters
        filters = FacetController.compute_active_filters(facet_state)
        
        # 3. SQL Slice Timeline
        t_sql_0 = time.time()
        photos_raw = self.slicer.slice_timeline(
            start_iso=filters.get("start_iso"),
            end_iso=filters.get("end_iso"),
            year=filters.get("year"),
            month=filters.get("month"),
            media_type=filters.get("media_type", "all"),
            location_name=filters.get("location_name")
        )
        sql_latency = time.time() - t_sql_0
        
        # 4. Widener (Graceful Fallback if neighborhood < 5)
        widened = False
        if len(photos_raw) < 5 and (filters.get("start_iso") or filters.get("year")):
            if filters.get("media_type") != "all" or filters.get("location_name"):
                photos_raw = self.slicer.slice_timeline(
                    start_iso=filters.get("start_iso"),
                    end_iso=filters.get("end_iso"),
                    year=filters.get("year"),
                    month=filters.get("month"),
                    media_type="all"
                )
                widened = True
                
        # 5. Baseline Rank
        search_clues = list(anchor.soft_visual_clues)
        if filters.get("location_name"):
            search_clues.append(filters["location_name"])
        if filters.get("event_tag"):
            search_clues.append(filters["event_tag"])
            
        scored = BaselineMatcher.rank_neighborhood(photos_raw, search_clues)
        
        processing_latency_ms = (time.time() - t0) * 1000
        
        target_found = any(p.photo.is_ground_truth_target for p in scored)
        scroll_depth = next((i for i, p in enumerate(scored) if p.photo.is_ground_truth_target), None)
        
        import calendar
        if filters.get("year") and filters.get("month") and 1 <= filters["month"] <= 12:
            m_name = calendar.month_name[filters["month"]]
            banner = f"Jumped to {m_name} {filters['year']} ({len(scored)} photos)"
        elif filters.get("year"):
            banner = f"Jumped to Year {filters['year']} ({len(scored)} photos)"
        elif filters.get("location_name"):
            banner = f"Jumped to {filters['location_name']} ({len(scored)} photos)"
        else:
            banner = f"Found {len(scored)} photos matching your criteria"
            
        return NeighborhoodResult(
            query_text=query,
            parsed_anchor=anchor,
            facet_chips=facet_state.chips,
            banner_text=banner,
            total_library_photos=self.slicer.count_total(),
            neighborhood_size=len(scored),
            widened_window=widened,
            photos=scored,
            target_photo_found=target_found,
            scroll_depth_to_target=scroll_depth,
            processing_latency_ms=processing_latency_ms
        )
