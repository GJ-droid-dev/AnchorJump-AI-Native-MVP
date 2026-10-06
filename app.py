import streamlit as st
import time
from core.config import Config
from core.llm_client import LLMClient
from engine.timeline_slicer import TimelineSlicer
from engine.hybrid_pipeline import HybridPipeline

st.set_page_config(page_title="AnchorJump MVP", layout="wide")

@st.cache_resource
def load_engine():
    slicer = TimelineSlicer(Config.LIBRARY_PATH)
    llm = LLMClient()
    pipeline = HybridPipeline(slicer, llm)
    return pipeline, slicer.count_total()

pipeline, total_photos = load_engine()

st.title("Google Photos: AnchorJump 📸")
st.caption(f"Hybrid Architecture MVP (Part 5) | Index: {total_photos} items | Reference Date: Oct 2026")

if "query" not in st.session_state:
    st.session_state.query = ""
if "facet_state" not in st.session_state:
    st.session_state.facet_state = None
if "result" not in st.session_state:
    st.session_state.result = None

def execute_search():
    if not st.session_state.query:
        return
    st.session_state.facet_state = None
    with st.spinner("Parsing anchor..."):
        res = pipeline.process_query(st.session_state.query, Config.REFERENCE_DATE, None)
        st.session_state.result = res
        from engine.facet_controller import FacetController
        st.session_state.facet_state = FacetController.init_from_anchor(res.parsed_anchor)

def execute_override():
    if not st.session_state.query or not st.session_state.facet_state:
        return
    res = pipeline.process_query(st.session_state.query, Config.REFERENCE_DATE, st.session_state.facet_state)
    st.session_state.result = res

col1, col2 = st.columns([3, 1])
with col1:
    st.text_input("Search photos (e.g., 'Goa March 2025 small cafe', 'screenshot 2025')", key="query", on_change=execute_search)
with col2:
    st.button("Search", on_click=execute_search, use_container_width=True)

if st.session_state.result and st.session_state.facet_state:
    res = st.session_state.result
    
    st.write("### Ambient Filters")
    if not st.session_state.facet_state.chips:
        st.caption("No temporal or media facets inferred.")
    else:
        chip_cols = st.columns(len(st.session_state.facet_state.chips) + 1)
        for idx, chip in enumerate(st.session_state.facet_state.chips):
            with chip_cols[idx]:
                is_active = st.checkbox(
                    f"{chip.label}", 
                    value=chip.is_active, 
                    key=f"chip_{chip.chip_id}_{res.query_text}"
                )
                if is_active != chip.is_active:
                    st.session_state.facet_state.chips[idx].is_active = is_active
                    execute_override()
                    st.rerun()

    if res.widened_window:
        st.warning(f"Neighborhood too small. Automatically widened search window. ({res.processing_latency_ms:.0f}ms)")
    else:
        st.success(f"{res.banner_text} ({res.processing_latency_ms:.0f}ms)")

    if not res.photos:
        st.info("No photos found in this chronological slice.")
    else:
        cols = st.columns(4)
        for i, scored in enumerate(res.photos):
            with cols[i % 4]:
                st.image(scored.photo.thumbnail_url, caption=f"{scored.photo.timestamp[:10]} | {scored.photo.location_name}")
                if scored.has_clue_highlight:
                    st.caption("✨ Clue Match")
                if scored.photo.is_ground_truth_target:
                    st.error("🎯 GROUND TRUTH TARGET")

