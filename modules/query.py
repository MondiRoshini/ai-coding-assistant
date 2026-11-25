import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from adaptive_prompt import get_level_instruction
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def run():
    st.markdown('<div class="premium-card"><h3>💬 Coding Chatbot</h3><p>Engage in a continuous discussion about programming. The assistant adapts to your skill level.</p></div>', unsafe_allow_html=True)

    # Get user level
    level = st.session_state.get(
        "skill_level",
        "Beginner"
    )

    # Initialize chat history
    if "query_messages" not in st.session_state:
        st.session_state.query_messages = []

    # Chat header controls
    col_level, col_clear = st.columns([4, 1])
    with col_level:
        st.markdown(f'<div class="level-badge">Adaptive Context: {level} Level</div>', unsafe_allow_html=True)
    with col_clear:
        if st.button("🗑️ Clear Chat", key="clear_query_chat", use_container_width=True):
            st.session_state.query_messages = []
            st.rerun()

    st.divider()

    # Display chat messages from history
    for message in st.session_state.query_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_input := st.chat_input("Ask a coding question..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add user message to chat history
        st.session_state.query_messages.append({"role": "user", "content": user_input})

        try:
            level_instruction = get_level_instruction(level)
            system_prompt = f"{level_instruction}\nYou are an expert programming chatbot tutor. Help the user learn coding concepts, debug their code, and solve problems."

            # Construct messages payload with system prompt
            messages_payload = [{"role": "system", "content": system_prompt}]
            
            # Add past chat history (up to last 15 messages to stay within context windows cleanly)
            history_window = st.session_state.query_messages[-14:] if len(st.session_state.query_messages) > 14 else st.session_state.query_messages
            for msg in history_window:
                messages_payload.append({"role": msg["role"], "content": msg["content"]})

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages_payload
                )

            answer = response.choices[0].message.content

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            # Add assistant response to chat history
            st.session_state.query_messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Error: {e}")
