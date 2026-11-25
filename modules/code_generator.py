import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from adaptive_prompt import get_level_instruction
from graphviz import Digraph
import keyword
import os
import html
import re

load_dotenv()

client = Groq(
api_key=os.getenv("GROQ_API_KEY")
)

KEYWORD_INFO = {
"if": "Used for decision making.",
"else": "Executes when the condition is false.",
"elif": "Checks another condition.",
"for": "Loop used to repeat code.",
"while": "Repeats code until a condition becomes false.",
"def": "Defines a function.",
"return": "Returns a value from a function.",
"class": "Defines a class.",
"import": "Imports a module.",
"try": "Starts exception handling.",
"except": "Handles exceptions.",
"break": "Stops a loop immediately.",
"continue": "Skips the current loop iteration.",
"pass": "Placeholder statement.",
"print": "Displays output.",
"range": "Generates a sequence of numbers."
}
def show_keyword_explanations(code):
    st.subheader("🔍 Keyword Explorer")

    found_keywords = []

    cleaned_code = (
        code.replace("(", " ")
            .replace(")", " ")
            .replace(":", " ")
            .replace(",", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("{", " ")
            .replace("}", " ")
    )

    for token in cleaned_code.split():
        token = token.strip()
        if token in KEYWORD_INFO:
            found_keywords.append(token)

    if not found_keywords:
        st.info("No major keywords detected.")
        return

    html = ""

    for kw in sorted(set(found_keywords)):
        html += (
            f"<span title=\"{KEYWORD_INFO[kw]}\" "
            "style=\"background:#e8f4ff; color:black; padding:8px; "
            "margin:5px; border-radius:6px; display:inline-block; "
            "cursor:pointer; font-weight:bold; border:1px solid #bcdcff;\">"
            f"{kw}</span>"
        )

    st.markdown(html, unsafe_allow_html=True)
    st.caption("Hover over a keyword to view its meaning and usage.")

def generate_flowchart(code):
    st.subheader("📊 Program Flowchart")

    lines = [line.strip() for line in code.split("\n") if line.strip()]

    if not lines:
        st.warning("No code available for flowchart generation.")
        return

    dot = Digraph()
    dot.attr(rankdir="TB")
    dot.node("Start", "Start", shape="oval")

    previous = "Start"
    count = 1

    for line in lines:
        node_id = f"N{count}"
        shape = "box"
        ls = line.lstrip()
        if ls.startswith("if") or ls.startswith("elif") or ls.startswith("for") or ls.startswith("while"):
            shape = "diamond"
        label = (line[:40] + "...") if len(line) > 40 else line
        dot.node(node_id, label, shape=shape)
def extract_code(text):
    # Regex to capture any content inside a triple backtick code block
    pattern = r"```(?:python|javascript|js)?\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    return None

def render_code_and_chart(code, language, level):
    # Prepare highlighted code with hoverable keywords
    escaped = html.escape(code)
    kw_list = sorted(KEYWORD_INFO.keys(), key=lambda x: -len(x))
    pattern = r"\b(" + "|".join(re.escape(k) for k in kw_list) + r")\b"

    def _replace_kw(m):
        k = m.group(0)
        title = KEYWORD_INFO.get(k, "")
        return f'<span title="{title}" style="background:#313244; color:#f5c2e7; border-radius:4px; padding:2px 4px; font-weight:bold; cursor:pointer;">{k}</span>'

    highlighted = re.sub(pattern, _replace_kw, escaped)

    col_code, col_chart = st.columns([5, 3])

    with col_code:
        st.markdown("##### ⚡ Active Generated Code")
        st.markdown(
            f"<div style=\"font-family:'JetBrains Mono', monospace; white-space:pre-wrap; font-size:13.5px; background:#1e1e2e; color:#cdd6f4; padding:20px; border-radius:12px; border:1px solid #313244; max-height:480px; overflow-y:auto; line-height:1.5;\">{highlighted}</div>",
            unsafe_allow_html=True,
        )

    with col_chart:
        st.markdown("##### 📊 Execution Flowchart")
        lines_for_chart = [ln.strip() for ln in code.split("\n") if ln.strip()]
        if not lines_for_chart:
            st.warning("No code available for flowchart generation.")
        else:
            compact = Digraph()
            compact.attr(rankdir="TB")
            compact.attr(size="4,4")
            compact.attr(bgcolor="transparent")
            compact.attr("node", fontsize="9", fontname="Outfit", style="filled")
            compact.attr("edge", color="#b4befe", arrowsize="0.7")
            
            # Draw start node
            compact.node("Start", "Start", shape="oval", fillcolor="#a6e3a1", fontcolor="#11111b")
            prev = "Start"
            i = 1
            for ln in lines_for_chart[:18]: # Cap chart depth to prevent visual clutter
                nid = f"C{i}"
                lab = (ln[:22] + "...") if len(ln) > 22 else ln
                
                ls = ln.lstrip()
                if ls.startswith(("if", "elif", "for", "while")):
                    shape = "diamond"
                    fill = "#f9e2af"
                    fontc = "#11111b"
                else:
                    shape = "box"
                    fill = "#1e1e2e"
                    fontc = "#cdd6f4"
                
                compact.node(nid, lab, shape=shape, fillcolor=fill, color="#b4befe", fontcolor=fontc)
                compact.edge(prev, nid)
                prev = nid
                i += 1

            if len(lines_for_chart) > 18:
                nid = "Truncated"
                compact.node(nid, f"... + {len(lines_for_chart) - 18} more lines", shape="box", fillcolor="#45475a", fontcolor="#cdd6f4")
                compact.edge(prev, nid)
                prev = nid

            compact.node("End", "End", shape="oval", fillcolor="#f38ba8", fontcolor="#11111b")
            compact.edge(prev, "End")
            st.graphviz_chart(compact, use_container_width=True)

    # Keywords explorer below code
    show_keyword_explanations(code)

def run():
    st.markdown('<div class="premium-card"><h3>💻 AI Code Generator</h3><p>Describe your requirements and generate structured code. Use the integrated chat below to request modifications or ask questions.</p></div>', unsafe_allow_html=True)

    level = st.session_state.get("skill_level", "Beginner")
    
    # Session state setup
    if "generator_code" not in st.session_state:
        st.session_state.generator_code = None
    if "generator_messages" not in st.session_state:
        st.session_state.generator_messages = []
    if "generator_lang" not in st.session_state:
        st.session_state.generator_lang = "Python"

    # Inputs layout
    col_lang, col_level = st.columns([3, 2])
    with col_lang:
        language = st.selectbox("Select Programming Language", ["Python", "JavaScript"], index=0 if st.session_state.generator_lang == "Python" else 1)
    with col_level:
        st.markdown(f'<div class="level-badge" style="margin-top: 28px;">Target Skill Level: {level}</div>', unsafe_allow_html=True)

    requirement = st.text_area("Describe what the code should do:", key="generator_req_input", height=100, placeholder="E.g., Write a function to check if a string is a palindrome...")

    if st.button("🚀 Generate Code", key="generate_btn", use_container_width=True):
        if not requirement.strip():
            st.warning("Please enter a requirement.")
            return

        # Update language in session state
        st.session_state.generator_lang = language

        if level == "Beginner":
            coding_style = """
Generate beginner-friendly code.
Requirements:
* Add detailed comments explaining every block
* Use highly descriptive variable names
* Keep logic simple and linear
* Avoid advanced paradigms
* Prioritize readability
"""
        elif level == "Intermediate":
            coding_style = """
Generate clean, structured code.
Requirements:
* Add useful comments explaining important functions
* Follow best practices and standard naming conventions
* Use functions when appropriate
* Balance readability and efficiency
"""
        else:
            coding_style = """
Generate production-quality code.
Requirements:
* Use standard industry best practices
* Optimize performance and complexity
* Follow clean code principles
* Use advanced techniques (e.g. error handling, type hints) when appropriate
* Minimize comments to only what is necessary
"""

        prompt = f"""
{coding_style}

Generate only {language} code.

Requirement:
{requirement}

Rules:
* Return code only
* Do not include markdown explanations
* Do not wrap code in explanations
"""

        try:
            with st.spinner("Generating code..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": coding_style},
                        {"role": "user", "content": prompt},
                    ],
                )

            generated_code = response.choices[0].message.content
            for marker in ("```python", "```javascript", "```js", "```"):
                generated_code = generated_code.replace(marker, "")
            generated_code = generated_code.strip()

            st.session_state.generator_code = generated_code
            
            # Initialize chat history
            st.session_state.generator_messages = [
                {"role": "user", "content": f"Generate {language} code for: {requirement}"},
                {"role": "assistant", "content": f"Here is the generated {language} code:\n\n```{language.lower()}\n{generated_code}\n```"}
            ]
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

    # Render Active Code Section if code exists
    if st.session_state.generator_code:
        st.markdown("---")
        render_code_and_chart(st.session_state.generator_code, st.session_state.generator_lang, level)
        
        st.markdown("---")
        st.markdown("#### 💬 Chat & Refine Code")
        st.caption("Ask questions, request modifications, or add features to the generated code.")

        # Show Chat History (skipping system notes, just user/assistant exchange)
        for msg in st.session_state.generator_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_prompt := st.chat_input("Ask for changes, e.g. 'write unit tests for this', 'make it recursive', 'add docstrings'"):
            # Display user query
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.generator_messages.append({"role": "user", "content": user_prompt})

            try:
                system_prompt = f"You are an expert developer assistant. You are helping a developer refine a {st.session_state.generator_lang} program. The level is {level}.\n" \
                                f"Always output code inside standard markdown code blocks with the language tag. " \
                                f"If you modify the code, provide the COMPLETE updated code inside a single code block so the visualizer can automatically update."

                messages_payload = [{"role": "system", "content": system_prompt}]
                # Gather recent context window
                history_window = st.session_state.generator_messages[-12:] if len(st.session_state.generator_messages) > 12 else st.session_state.generator_messages
                for msg in history_window:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                with st.spinner("Refining..."):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages_payload,
                    )

                reply = response.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.generator_messages.append({"role": "assistant", "content": reply})

                # Check if assistant returned new code and extract it to update visualization
                new_code = extract_code(reply)
                if new_code:
                    st.session_state.generator_code = new_code
                
                st.rerun()

            except Exception as e:
                st.error(f"Error calling model: {e}")
