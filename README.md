# 🔐 AI Escape Room — The Locked Victorian Library

An interactive natural-language Escape Room built with **Python**, **Streamlit**, and the **Google Gemini API (`google-genai`)**. The repository demonstrates the architectural evolution from a purely prompt-driven LLM prototype (**Version 1**) to a deterministic, state-validated neuro-symbolic game engine (**Version 2**).

## 🎯 Problem & Solution
- **Problem:** Pure LLM game masters suffer from state drift, hallucinated items, sycophancy (accepting false player claims), and prompt-injection vulnerabilities that leak secret codes.
- **Solution:** Version 2 decouples language understanding/narration from game logic. Gemini parses player intent into structured JSON and narrates outcomes, while a Python state engine (`EscapeRoomEngine`) and external JSON configuration (`room_config.json`) enforce inventory rules, puzzle dependencies, and lock combinations.

## 🏗️ Architecture Overview
- **Version 1 (`v1_basic/`):** Single-loop chat pipeline where Gemini manages narrative and implicit game state via conversation history.
- **Version 2 (`v2_reliable/`):** Three-stage pipeline:
  1. **Intent Parser (Gemini Structured Output):** Maps free-text commands into validated action schemas.
  2. **Deterministic Engine (`game_engine.py`):** Validates inventory, checks codes against `room_config.json`, and updates state.
  3. **Grounded Narrator (Gemini):** Generates story responses strictly from verified engine outcomes without access to secret codes.

*(See `docs/architecture.md` for system diagrams.)*

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/AI-Escape-Room.git
   cd AI-Escape-Room
