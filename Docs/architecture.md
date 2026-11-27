flowchart TD
    U[Player] -->|Natural Language| UI[Streamlit UI + State Sidebar]
    UI -->|Raw Input| P[LLM Intent Parser\nStructured JSON]
    P -->|action, target, code, item| E[Python Game Engine\nEscapeRoomEngine]
    C[(room_config.json\nRules & Secret Codes)] --> E
    S[(Structured Game State\nInventory, Clues, Locks)] <--> E
    E -->|Verified Outcome JSON| N[LLM Narrator\nGrounded Response]
    N -->|Atmospheric Text| UI
    UI -->|Story + Live State| U
