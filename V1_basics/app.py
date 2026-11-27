import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="AI Escape Room — Version 1", page_icon="🔐")

SYSTEM_PROMPT_V1 = """
You are the Game Master of an interactive Escape Room set inside a locked Victorian Library.
Your job is to describe the environment immersively, respond to the player's actions, and guide the story without giving away solutions directly.

ROOM & PUZZLE DESIGN (Keep consistent):
1. Room: A locked library with 5 interactive objects:
   - Wooden Desk (has a locked drawer requiring a 3-digit code: 419, and a magnifying glass resting on top).
   - Oak Bookshelf (contains four leather-bound volumes slightly pulled out; inspecting them reveals handwritten numbers: 4, 1, 9).
   - Oil Painting (depicts a clock tower; examining it closely or with the magnifying glass reveals Roman numeral VII = 7 carved in the corner).
   - Locked Desk Drawer (opens with code 419; contains a Brass Key and a torn note reading: "Combine the drawer digits with the painting's hour at the end").
   - Heavy Iron Exit Door (secured by a 4-digit keypad; requires code 4197 to unlock).
2. Rules:
   - Let the player examine objects, pick up items, solve clues, and try codes.
   - Track what the player has found and unlocked based on conversation history.
   - When the player enters 4197 on the exit door, congratulate them and clearly state: "CONGRATULATIONS! YOU HAVE ESCAPED!"
   - Keep responses atmospheric, concise (3-5 sentences), and always end by prompting what the player wants to do next.
"""

def init_v1():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing GEMINI_API_KEY in .env file.")
        st.stop()
    st.session_state.client_v1 = genai.Client(api_key=api_key)
    st.session_state.messages_v1 = [
        {
            "role": "assistant",
            "content": (
                "You wake up on the cold rug of a dimly lit Victorian library. The heavy iron exit door is sealed "
                "with a 4-digit electronic keypad. Around the room you see a **wooden desk**, a towering **oak bookshelf**, "
                "an **oil painting** on the wall, and a **locked drawer** built into the desk.\n\n"
                "*Type what you would like to examine or do (e.g., 'examine the desk', 'inspect the bookshelf').*"
            ),
        }
    ]

if "messages_v1" not in st.session_state:
    init_v1()

with st.sidebar:
    st.title("🔐 Escape Room (V1)")
    st.markdown(
        "**How to Play:**\n"
        "- Explore the room using natural language.\n"
        "- Examine all 5 objects to uncover clues.\n"
        "- Unlock the 4-digit exit door to escape."
    )
    if st.button("🔄 Restart Game", use_container_width=True):
        init_v1()
        st.rerun()

st.title("🔐 The Locked Library — Version 1 (LLM-Driven)")

for msg in st.session_state.messages_v1:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("What do you do?"):
    st.session_state.messages_v1.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in st.session_state.messages_v1
    ]

    response = st.session_state.client_v1.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_V1,
            temperature=0.7,
        ),
    )

    reply = response.text
    st.session_state.messages_v1.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
