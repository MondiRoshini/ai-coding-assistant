import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from adaptive_prompt import get_level_instruction
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

EXPLAIN_PROMPT = """
{level_instruction}

You are an expert programming tutor.

Explain the following code line by line.

Code:
{code}

Format:

Line 1:
Explanation

Line 2:
Explanation

...

At the end provide:
- Overall purpose
- Time complexity (if applicable)
- Space complexity (if applicable)
"""

SIMPLE_PROMPT = """
You are teaching programming to a complete beginner.

Explain the following code in very simple English.

Code:
{code}

Requirements:
- Avoid technical jargon
- Use simple examples
- Explain what each line does
- Keep it easy to understand
"""


def run():
    st.markdown('<div class="premium-card"><h3>📖 Code Explanation Engine</h3><p>Paste your code to get a detailed line-by-line breakdown, and ask follow-up questions to understand it deeply.</p></div>', unsafe_allow_html=True)

    level = st.session_state.get("skill_level", "Beginner")

    # Initialize states
    if "explainer_code" not in st.session_state:
        st.session_state.explainer_code = None
    if "explainer_explanation" not in st.session_state:
        st.session_state.explainer_explanation = None
    if "explainer_messages" not in st.session_state:
        st.session_state.explainer_messages = []

    # Code input box
    code_input = st.text_area(
        "Paste your code here:",
        height=180,
        key="code_to_explain_input",
        placeholder="Paste your Python or JavaScript code here..."
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        explain_btn = st.button("📖 Explain Code", key="explain_btn", use_container_width=True)
    with col2:
        simple_btn = st.button("🧸 Simpler Explanation", key="simple_btn", use_container_width=True)
    with col3:
        st.markdown(f'<div class="level-badge" style="text-align:center; width:100%; margin-top:2px;">Context: {level}</div>', unsafe_allow_html=True)

    # Process new request
    if (explain_btn or simple_btn) and code_input.strip():
        st.session_state.explainer_code = code_input.strip()
        
        try:
            level_instruction = get_level_instruction(level)
            if explain_btn:
                prompt = EXPLAIN_PROMPT.format(
                    code=code_input,
                    level_instruction=level_instruction
                )
                system_content = level_instruction
            else:
                prompt = SIMPLE_PROMPT.format(
                    code=code_input
                )
                system_content = "You are teaching programming to a complete beginner."

            with st.spinner("Analyzing code..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt}
                    ]
                )

            explanation = response.choices[0].message.content
            st.session_state.explainer_explanation = explanation
            
            # Setup chat history starting with this explanation
            st.session_state.explainer_messages = [
                {"role": "user", "content": f"Explain the following code:\n```\n{code_input}\n```"},
                {"role": "assistant", "content": explanation}
            ]
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

    # Display results and chat side-by-side/stacked
    if st.session_state.explainer_explanation:
        st.markdown("---")
        st.subheader("📝 Analysis Results")
        
        col_code, col_exp = st.columns([2, 3])
        
        with col_code:
            st.markdown("**Original Code:**")
            st.code(st.session_state.explainer_code, language="python" if "def " in st.session_state.explainer_code or "import " in st.session_state.explainer_code else "javascript")
            
        with col_exp:
            st.markdown("**AI Explanation:**")
            with st.container(border=True):
                st.markdown(st.session_state.explainer_explanation)

        st.markdown("---")
        st.markdown("#### 💬 Chat & Clarify Explanation")
        st.caption("Ask follow-up questions to clarify concepts or lines of code.")

        # Show Chat history
        for msg in st.session_state.explainer_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_prompt := st.chat_input("Ask a follow-up question..."):
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.explainer_messages.append({"role": "user", "content": user_prompt})

            try:
                system_prompt = f"You are an expert programming tutor assisting a student at a {level} level.\n" \
                                f"Answer the user's follow-up questions regarding the code they provided and the explanation you gave."

                messages_payload = [{"role": "system", "content": system_prompt}]
                # Gather recent context
                history_window = st.session_state.explainer_messages[-10:] if len(st.session_state.explainer_messages) > 10 else st.session_state.explainer_messages
                for msg in history_window:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                with st.spinner("Answering..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages_payload
                    )

                reply = response.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.explainer_messages.append({"role": "assistant", "content": reply})
                st.rerun()

            except Exception as e:
                st.error(f"Error calling model: {e}")
