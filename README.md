# Google Photos AnchorJump — AI-Native Memory Retrieval MVP

> **A Hybrid Architecture for Vague-Memory Retrieval: AI Semantic Ingestion with Ambient Facet Overrides**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-Gemini_3.8_Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![Framework](https://img.shields.io/badge/UI-Streamlit_1.30-red.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Engine-SQLite_In--Memory-green.svg)](https://www.sqlite.org/)

---

## 🌐 Live Interactive Prototype

The prototype is deployed and can be tested immediately in your browser:
👉 **[Launch AnchorJump on Streamlit Community Cloud](https://anchorjump-ai-native-mvp-2mdrty4zrns2gzvpkwuith.streamlit.app/)**

---

## 🚀 Overview

**AnchorJump** translates vague, incomplete human episodic recall (e.g., *"Goa trip March 2025 small cafe"*, *"London 2024 july"*, *"screenshot medicine last December"*) into a tight, chronologically bounded photo neighborhood in Google Photos.

### The Hybrid Architecture
1. **AI Semantic Ingestion (Gemini 3.8 Flash):** Parses approximate natural language queries into structured temporal/spatial bounds.
2. **Chronological Timeline Slicer (SQLite):** Slices an arm's-reach photo neighborhood (<15–25 photos) in strict chronological sequence.
3. **Ambient Facet Controller:** Automatically projects AI-parsed parameters into interactive, auto-populated filter chips (`[📅 2024]`, `[📅 July]`, `[📍 London]`, `[📷 Photos]`).
4. **Sub-50ms Tactile Overrides:** Users can adjust any chip in 1 tap, instantly re-slicing the timeline locally without re-invoking the LLM.

---

## 🧪 Testing the Prototype

### Quick Test Queries
- **Canonical Episodic Memory:** `"Goa March 2025 small cafe"` $\rightarrow$ lands on March 2025 Goa trip slice; target café is Photo #4.
- **Tactile Month/Year Override:** `"London 2024 july"` $\rightarrow$ tap the `[📅 July ▾]` chip, switch to August in 1 click (sub-50ms local SQL re-slicing).
- **Utility Document:** `"screenshot medicine last December"` $\rightarrow$ isolates December prescription screenshots.
- **Relative Time Anchor:** `"Thanksgiving around 5 years ago"` $\rightarrow$ jumps to Thanksgiving 2021 burst.

---

## 🛠️ Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd google-photos-anchorjump

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Or on Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
# Add your GEMINI_API_KEY in .env

# Run Streamlit App
streamlit run app.py
```

---

## ☁️ Streamlit Cloud Deployment

When deploying to [Streamlit Community Cloud](https://share.streamlit.io):
1. **Repository:** Select your GitHub repo (`google-photos-anchorjump` or root repo).
2. **Main file path:** `app.py`
3. **App Settings > Secrets:**
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   ```
4. Click **Deploy!**
