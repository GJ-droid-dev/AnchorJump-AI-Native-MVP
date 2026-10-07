import streamlit as st
import calendar
from typing import Callable, Optional
from core.schemas import FacetOverrideState, FacetChip
from engine.facet_controller import FacetController

MONTH_OPTIONS = [
    "Auto / Any Month", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

YEAR_OPTIONS = ["Auto / Any Year", "2026", "2025", "2024", "2023", "2022", "2021"]

MEDIA_DISPLAY_MAP = {
    "all": "All Media",
    "photo": "Photo",
    "screenshot": "Screenshot",
    "receipt": "Receipt",
    "document": "Document"
}
REV_MEDIA_MAP = {v: k for k, v in MEDIA_DISPLAY_MAP.items()}
MEDIA_OPTIONS = ["All Media", "Photo", "Screenshot", "Receipt", "Document"]

LOCATION_OPTIONS = [
    "Auto / Any Location", "Goa, India", "London, UK", "Boston, MA", "Chicago, IL",
    "Miami, FL", "New York, NY", "Paris, France", "San Francisco, CA",
    "Sydney, Australia", "Tokyo, Japan", "Home", "Office"
]

def render_ambient_filters(
    facet_state: FacetOverrideState,
    query_id: str,
    on_override: Callable[[], None],
    on_reset: Optional[Callable[[], None]] = None
):
    """
    Renders the Ambient Filters dropdown expander containing 1-tap tactile dropdown overrides
    ([📅 Year ▾], [📅 Month ▾], [📷 Media Type ▾], [📍 Location ▾]) for sub-50ms local SQLite re-slicing.
    """
    if not facet_state:
        return

    reset_count = st.session_state.get("reset_count", 0)
    full_id = f"{query_id}_{reset_count}"

    # Compute current active filters
    active_filters = FacetController.compute_active_filters(facet_state)
    curr_year = active_filters.get("year")
    curr_month = active_filters.get("month")
    curr_media = active_filters.get("media_type") or "all"
    curr_loc = active_filters.get("location_name")

    # Format chips preview badges
    chips_html = []
    if curr_year:
        chips_html.append(f"`[📅 {curr_year} ▾]`")
    if curr_month and 1 <= curr_month <= 12:
        chips_html.append(f"`[📅 {calendar.month_name[curr_month]} ▾]`")
    if curr_media and curr_media != "all":
        chips_html.append(f"`[📷 {curr_media.capitalize()} ▾]`")
    if curr_loc:
        chips_html.append(f"`[📍 {curr_loc} ▾]`")

    chip_summary = " &nbsp; ".join(chips_html) if chips_html else "*No explicit filters active (browsing full slice)*"

    with st.expander("🏷️ Ambient Filters ▾ (AI Parsed & 1-Tap Tactile Overrides)", expanded=True):
        st.markdown(f"**Active Ambient Chips:** &nbsp; {chip_summary}")
        st.caption("AI-inferred parameters from Gemini 3.8 Flash. Select any dropdown to override locally in <50ms without re-querying the cloud LLM:")

        col1, col2, col3, col4 = st.columns(4)

        # 1. Year Dropdown
        with col1:
            default_year_idx = 0
            if curr_year:
                year_str = str(curr_year)
                if year_str in YEAR_OPTIONS:
                    default_year_idx = YEAR_OPTIONS.index(year_str)

            year_key = f"sel_year_{full_id}"
            def on_year_change():
                val = st.session_state[year_key]
                target = int(val) if val != "Auto / Any Year" else None
                facet_state.active_overrides["year"] = target
                # Sync chip
                chip = next((c for c in facet_state.chips if c.category == "year"), None)
                if chip:
                    if target:
                        chip.value = target
                        chip.label = str(target)
                        chip.is_active = True
                    else:
                        chip.is_active = False
                elif target:
                    facet_state.chips.append(FacetChip(chip_id="override_year", category="year", label=str(target), value=target))
                on_override()

            st.selectbox(
                "📅 Year ▾",
                options=YEAR_OPTIONS,
                index=default_year_idx,
                key=year_key,
                on_change=on_year_change
            )

        # 2. Month Dropdown
        with col2:
            default_month_idx = 0
            if curr_month and 1 <= curr_month <= 12:
                m_name = calendar.month_name[curr_month]
                if m_name in MONTH_OPTIONS:
                    default_month_idx = MONTH_OPTIONS.index(m_name)

            month_key = f"sel_month_{full_id}"
            def on_month_change():
                val = st.session_state[month_key]
                target = MONTH_OPTIONS.index(val) if val != "Auto / Any Month" else None
                facet_state.active_overrides["month"] = target
                # Sync chip
                chip = next((c for c in facet_state.chips if c.category == "month"), None)
                if chip:
                    if target:
                        chip.value = target
                        chip.label = calendar.month_name[target]
                        chip.is_active = True
                    else:
                        chip.is_active = False
                elif target:
                    facet_state.chips.append(FacetChip(chip_id="override_month", category="month", label=calendar.month_name[target], value=target))
                on_override()

            st.selectbox(
                "📅 Month ▾",
                options=MONTH_OPTIONS,
                index=default_month_idx,
                key=month_key,
                on_change=on_month_change
            )

        # 3. Media Type Dropdown
        with col3:
            curr_media_label = MEDIA_DISPLAY_MAP.get(curr_media.lower(), "All Media")
            default_media_idx = MEDIA_OPTIONS.index(curr_media_label) if curr_media_label in MEDIA_OPTIONS else 0

            media_key = f"sel_media_{full_id}"
            def on_media_change():
                val = st.session_state[media_key]
                target = REV_MEDIA_MAP.get(val, "all")
                facet_state.active_overrides["media_type"] = target
                # Sync chip
                chip = next((c for c in facet_state.chips if c.category == "media_type"), None)
                if chip:
                    if target != "all":
                        chip.value = target
                        chip.label = val
                        chip.is_active = True
                    else:
                        chip.is_active = False
                elif target != "all":
                    facet_state.chips.append(FacetChip(chip_id="override_media", category="media_type", label=val, value=target))
                on_override()

            st.selectbox(
                "📷 Media Type ▾",
                options=MEDIA_OPTIONS,
                index=default_media_idx,
                key=media_key,
                on_change=on_media_change
            )

        # 4. Location Dropdown
        with col4:
            default_loc_idx = 0
            if curr_loc:
                for idx, loc_opt in enumerate(LOCATION_OPTIONS):
                    if curr_loc.lower() in loc_opt.lower() or loc_opt.lower() in curr_loc.lower():
                        default_loc_idx = idx
                        break

            loc_key = f"sel_loc_{full_id}"
            def on_loc_change():
                val = st.session_state[loc_key]
                target = val if val != "Auto / Any Location" else None
                facet_state.active_overrides["location_name"] = target
                # Sync chip
                chip = next((c for c in facet_state.chips if c.category == "location"), None)
                if chip:
                    if target:
                        chip.value = target
                        chip.label = target
                        chip.is_active = True
                    else:
                        chip.is_active = False
                elif target:
                    facet_state.chips.append(FacetChip(chip_id="override_loc", category="location", label=target, value=target))
                on_override()

            st.selectbox(
                "📍 Location ▾",
                options=LOCATION_OPTIONS,
                index=default_loc_idx,
                key=loc_key,
                on_change=on_loc_change
            )

        # Action bar
        act_c1, act_c2 = st.columns([1, 4])
        with act_c1:
            if on_reset:
                st.button(
                    "🔄 Reset to AI Defaults", 
                    key=f"reset_{full_id}", 
                    on_click=on_reset, 
                    use_container_width=True
                )
