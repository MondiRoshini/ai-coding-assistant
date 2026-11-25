import streamlit as st
from syntax import check_syntax
from lint import run_pyflakes
from ai_fixer import get_fix
from adaptive_prompt import get_level_instruction
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def run():
    st.markdown('<div class="premium-card"><h3>🐞 Python Error Detector & Fixer</h3><p>Paste your Python code to run syntax checks, static analysis linting, and runtime checks. Discuss and debug issues with the assistant below.</p></div>', unsafe_allow_html=True)

    level = st.session_state.get("skill_level", "Beginner")

    # Initialize states
    if "detector_code" not in st.session_state:
        st.session_state.detector_code = None
    if "detector_results" not in st.session_state:
        st.session_state.detector_results = None
    if "detector_messages" not in st.session_state:
        st.session_state.detector_messages = []

    # Code input
    code_input = st.text_area(
        "Paste Python Code:",
        height=200,
        key="code_to_detect_input",
        placeholder="Paste your Python code here..."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_btn = st.button("🔍 Analyze Code", key="analyze_code_btn", use_container_width=True)
    with col2:
        st.markdown(f'<div class="level-badge" style="text-align:center; width:100%; margin-top:2px;">Context: {level}</div>', unsafe_allow_html=True)

    if analyze_btn and code_input.strip():
        code = code_input.strip()
        st.session_state.detector_code = code
        level_instruction = get_level_instruction(level)
        
        diagnostics = []
        is_clean = True
        fix_content = ""
        
        # 1. Syntax Check
        syntax_error = check_syntax(code)
        if syntax_error:
            diagnostics.append({"type": "Syntax Error", "detail": syntax_error, "status": "error"})
            is_clean = False
            fix_content = get_fix(code, f"{level_instruction}\nError Type: Syntax Error\n{syntax_error}")
        else:
            diagnostics.append({"type": "Syntax Check", "detail": "No Syntax Errors Found", "status": "success"})
            
            # 2. Lint Check
            lint_errors = run_pyflakes(code)
            if lint_errors and lint_errors != "No issues found":
                diagnostics.append({"type": "Lint Issue", "detail": lint_errors, "status": "error"})
                is_clean = False
                fix_content = get_fix(code, f"{level_instruction}\nError Type: Lint Error\n{lint_errors}")
            else:
                diagnostics.append({"type": "Lint Check", "detail": "No Lint Issues Found", "status": "success"})
                
                # 3. Runtime Check
                try:
                    exec(code, {})
                    diagnostics.append({"type": "Runtime Check", "detail": "No Runtime Errors Found", "status": "success"})
                except Exception as e:
                    runtime_error = f"{type(e).__name__}: {e}"
                    diagnostics.append({"type": "Runtime Error", "detail": runtime_error, "status": "error"})
                    is_clean = False
                    fix_content = get_fix(code, f"{level_instruction}\nError Type: Runtime Error\n{runtime_error}")

        # 4. Logical Analysis
        logical_analysis = ""
        if is_clean:
            if level == "Beginner":
                logical_prompt = "Analyze this code.\nRequirements:\n- Explain simply\n- Mention logical mistakes\n- Explain why they happen\n- Show beginner-friendly fixes\n- Suggest improvements\n"
            elif level == "Intermediate":
                logical_prompt = "Analyze this code.\nRequirements:\n- Find logical errors\n- Identify edge cases\n- Suggest cleaner implementations\n- Discuss complexity if relevant\n"
            else:
                logical_prompt = "Perform an advanced code review.\nRequirements:\n- Detect logical flaws\n- Identify algorithmic weaknesses\n- Discuss complexity\n- Suggest optimizations\n- Mention scalability concerns\n- Suggest production-grade improvements\n"
            
            with st.spinner("Performing logical review..."):
                logical_analysis = get_fix(code, logical_prompt)

        # Store results
        results = {
            "diagnostics": diagnostics,
            "is_clean": is_clean,
            "fix_content": fix_content,
            "logical_analysis": logical_analysis
        }
        st.session_state.detector_results = results

        # Create history summary
        summary_lines = []
        for d in diagnostics:
            symbol = "❌" if d["status"] == "error" else "✅"
            summary_lines.append(f"{symbol} **{d['type']}**: {d['detail']}")
        
        history_response = "\n".join(summary_lines)
        if fix_content:
            history_response += f"\n\n### Suggested Fix:\n{fix_content}"
        if logical_analysis:
            history_response += f"\n\n### Logical Analysis:\n{logical_analysis}"

        st.session_state.detector_messages = [
            {"role": "user", "content": f"Analyze this Python code for errors:\n```python\n{code}\n```"},
            {"role": "assistant", "content": f"Here is the error analysis findings:\n\n{history_response}"}
        ]
        st.rerun()

    # Display results and chat
    if st.session_state.detector_results:
        st.markdown("---")
        st.subheader("📝 Diagnostic Findings")
        
        res = st.session_state.detector_results
        col_code, col_diag = st.columns([2, 3])
        
        with col_code:
            st.markdown("**Analyzed Code:**")
            st.code(st.session_state.detector_code, language="python")
            
        with col_diag:
            st.markdown("**Diagnostic Checks:**")
            for d in res["diagnostics"]:
                if d["status"] == "error":
                    st.error(f"**{d['type']}**\n{d['detail']}")
                else:
                    st.success(f"**{d['type']}** - {d['detail']}")
                    
            if res["fix_content"]:
                st.markdown("**Suggested Correction:**")
                with st.container(border=True):
                    st.markdown(res["fix_content"])
            elif res["logical_analysis"]:
                st.markdown("**Logical Review:**")
                with st.container(border=True):
                    st.markdown(res["logical_analysis"])

        st.markdown("---")
        st.markdown("#### 💬 Chat & Discuss Bugs")
        st.caption("Ask questions about the errors, the fix, or general debugging strategies.")

        # Show Chat History
        for msg in st.session_state.detector_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_prompt := st.chat_input("Ask a follow-up debugging question..."):
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.detector_messages.append({"role": "user", "content": user_prompt})

            try:
                system_prompt = f"You are an expert Python debugging assistant. The user is at a {level} skill level.\n" \
                                f"Explain the errors, logical flow, and suggestions for the Python program provided."

                messages_payload = [{"role": "system", "content": system_prompt}]
                # Gather recent context
                history_window = st.session_state.detector_messages[-10:] if len(st.session_state.detector_messages) > 10 else st.session_state.detector_messages
                for msg in history_window:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                with st.spinner("Debugging..."):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages_payload
                    )

                reply = response.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.detector_messages.append({"role": "assistant", "content": reply})
                st.rerun()

            except Exception as e:
                st.error(f"Error calling model: {e}")