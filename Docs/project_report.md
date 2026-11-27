# Design and Reliability Engineering of an AI-Powered Escape Room

## 1. Introduction and Objectives
Large Language Models (LLMs) excel at open-ended interactive storytelling, making them natural candidates for text-based adventure games. However, relying purely on an LLM to enforce game rules introduces state drift, hallucinated inventory, and vulnerability to prompt injection. This project implements an interactive Escape Room ("The Locked Victorian Library") in two stages: **Version 1**, a conversational LLM-driven prototype, and **Version 2**, a hybrid neuro-symbolic architecture combining deterministic Python state validation with Gemini-powered natural-language understanding and narration.

## 2. Game Design and Puzzle Structure
The scenario places the player inside a locked Victorian library containing five interactive entities and a multi-step causal puzzle chain:
1. **Wooden Desk:** Holds a collectable brass magnifying glass and houses a 3-digit locked drawer.
2. **Oak Bookshelf:** Contains three displaced leather-bound books inscribed with the digits `4`, `1`, and `9`.
3. **Locked Drawer:** Requires the bookshelf combination (`419`) and contains a torn note instructing the player to append the painting's hour to the drawer digits.
4. **Oil Painting:** Depicts a clock tower whose corner inscription (`Hour VII` / `7`) is readable only after collecting and using the magnifying glass.
5. **Heavy Iron Exit Door:** Secured by a 4-digit keypad requiring `4197` (`419` + `7`) to win the game.

## 3. Version 1 Implementation and Limitations
Version 1 uses Streamlit for the chat interface and the `google-genai` SDK (`gemini-2.5-flash`) with a comprehensive system prompt containing the room layout, puzzle rules, and secret codes. The full conversation history is sent on each turn so the model can infer game progress.

During testing, four core reliability failures emerged:
- **Context & State Drift:** Over multi-turn sessions, the LLM occasionally forgot whether the drawer was already open or whether the magnifying glass had been picked up.
- **Hallucinated Affordances:** When players referenced objects not in the room (e.g., a window or rug), the LLM improvised new items that diluted the puzzle path.
- **Sycophancy & False Claims:** If a player asserted that they had already solved a clue, the model frequently agreed to remain helpful.
- **Prompt Injection & Secret Leakage:** Because secret combinations (`419` and `4197`) were stored directly inside the system prompt, administrator impersonation or jailbreak prompts could coax the model into revealing codes or unlocking the exit prematurely.

## 4. Version 2 Architecture and Improvements
To eliminate these failure modes, Version 2 separates **language processing** from **game state and rule enforcement**:
1. **Externalized Configuration (`room_config.json`):** All objects, clue dependencies, and secret codes are stored in structured JSON outside the LLM prompts.
2. **Structured Intent Parsing:** Player input is first passed to Gemini with `response_schema=PlayerIntent` (`temperature=0.0`), translating free-form phrasing into canonical actions (`examine`, `take`, `use_item`, `unlock_drawer`, `unlock_door`) or flagging adversarial patterns (`admin_override`, `reveal_secrets`, `claim_solved`).
3. **Deterministic Python Engine (`EscapeRoomEngine`):** Python functions verify inventory prerequisites (requiring `magnifying_glass` before reading the painting), validate exact numeric combinations, mutate `state` dictionaries, and block unauthorized actions.
4. **Grounded Narration:** Gemini receives only the validated `[ENGINE_RESULT]` JSON and public state—never the secret codes—to generate immersive feedback.

## 5. Evaluation Summary and Conclusion
Across six structured test cases (including uncollected item usage, wrong combinations, false solved claims, administrator impersonation, code extraction, and nonexistent objects), Version 1 failed 5 of 6 edge/adversarial scenarios, whereas Version 2 enforced 100% rule compliance without state corruption. Separating deterministic state management from generative narration provides a robust blueprint for trustworthy LLM applications.
