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

from components.facet_chips import render_ambient_filters

def execute_override():
    if not st.session_state.query or not st.session_state.facet_state:
        return
    res = pipeline.process_query(
        st.session_state.query, 
        Config.REFERENCE_DATE, 
        st.session_state.facet_state,
        parsed_anchor=st.session_state.result.parsed_anchor if st.session_state.result else None
    )
    st.session_state.result = res

def reset_to_inferred():
    if not st.session_state.result or not st.session_state.result.parsed_anchor:
        return
    from engine.facet_controller import FacetController
    st.session_state.facet_state = FacetController.init_from_anchor(st.session_state.result.parsed_anchor)
    execute_override()

col1, col2 = st.columns([3, 1])
with col1:
    st.text_input("Search photos (e.g., 'Goa March 2025 small cafe', 'screenshot 2025')", key="query", on_change=execute_search)
with col2:
    st.button("Search", on_click=execute_search, use_container_width=True)

st.write("##### ⚡ Quick Benchmark Scenarios:")
quick_cols = st.columns(4)
benchmarks = [
    ("🏖️ Goa Café 2025", "Goa March 2025 small cafe"),
    ("🇬🇧 London July 2024", "London 2024 july"),
    ("💊 Medicine Screenshot", "screenshot medicine last December"),
    ("🦃 Thanksgiving 2021", "Thanksgiving 2021 family reunion")
]
for i, (label, b_query) in enumerate(benchmarks):
    with quick_cols[i]:
        if st.button(label, key=f"bench_{i}", use_container_width=True):
            st.session_state.query = b_query
            execute_search()
            st.rerun()

if st.session_state.result and st.session_state.facet_state:
    res = st.session_state.result
    
    query_id = str(abs(hash(res.query_text)))
    render_ambient_filters(
        st.session_state.facet_state,
        query_id=query_id,
        on_override=execute_override,
        on_reset=reset_to_inferred
    )

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

