from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class TemporalAnchor(BaseModel):
    raw_text: str = Field(description="Raw temporal substring from the query")
    anchor_type: Literal[
        "exact_date", "month_year", "year_only", "relative_offset", 
        "season_year", "holiday_event", "none"
    ]
    resolved_start_iso: Optional[str] = Field(None, description="ISO 8601 start timestamp")
    resolved_end_iso: Optional[str] = Field(None, description="ISO 8601 end timestamp")
    confidence: float = Field(ge=0.0, le=1.0)

class ParsedAnchor(BaseModel):
    has_anchor: bool = Field(description="True if query contains any usable episodic anchor")
    temporal: Optional[TemporalAnchor] = None
    event_tag: Optional[str] = Field(None, description="Named event/trip (e.g., 'Goa trip', 'wedding')")
    location_name: Optional[str] = Field(None, description="Approximate place name")
    media_type: Literal["all", "photo", "screenshot", "receipt", "document"] = "all"
    people_tags: List[str] = Field(default_factory=list)
    soft_visual_clues: List[str] = Field(
        default_factory=list, 
        description="Secondary visual descriptors (colors, objects, scene elements) for in-neighborhood ranking"
    )
    parsing_latency_ms: Optional[float] = None

class FacetChip(BaseModel):
    chip_id: str
    category: Literal["year", "month", "location", "media_type", "event", "clue"]
    label: str                   # e.g., "2024", "July", "Goa", "Photos", "Café"
    value: Any                   # Resolved value or range
    is_active: bool = True       # Can be toggled on/off
    can_override: bool = True    # Opens modal or picker to change value

class FacetOverrideState(BaseModel):
    chips: List[FacetChip] = Field(default_factory=list)
    active_overrides: Dict[str, Any] = Field(default_factory=dict)

class PhotoRecord(BaseModel):
    photo_id: str
    timestamp: str  # ISO 8601 string: YYYY-MM-DDTHH:MM:SSZ
    media_type: Literal["photo", "screenshot", "receipt", "document"]
    event_tag: Optional[str] = None
    location_name: str
    latitude: float
    longitude: float
    people: List[str] = Field(default_factory=list)
    caption: str
    ocr_text: Optional[str] = None
    visual_tags: List[str] = Field(default_factory=list)
    thumbnail_url: str
    is_ground_truth_target: Optional[bool] = False
    ground_truth_scenario_id: Optional[str] = None

class ScoredPhoto(BaseModel):
    photo: PhotoRecord
    in_neighborhood_rank: int
    semantic_score: float = Field(ge=0.0, le=1.0)
    has_clue_highlight: bool = False
    highlight_badge_text: Optional[str] = None

class NeighborhoodResult(BaseModel):
    query_text: str
    parsed_anchor: ParsedAnchor
    facet_chips: List[FacetChip]
    banner_text: str
    total_library_photos: int
    neighborhood_size: int
    widened_window: bool
    widened_explanation: Optional[str] = None
    photos: List[ScoredPhoto]
    target_photo_found: bool
    scroll_depth_to_target: Optional[int] = None
    processing_latency_ms: float
