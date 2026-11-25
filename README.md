# 🤖 AI Coding Assistant

An adaptive, interactive AI-powered coding tutor and assistant built with **Streamlit** and powered by **Groq (`llama-3.1-8b-instant`)**. It dynamically adjusts code generation, explanations, and diagnostics to match the user's skill level (Beginner, Intermediate, Advanced) and supports continuous multi-turn chat across all modules.

---

## ✨ Features

- **🎯 Adaptive Skill Profiles:** Choose between Beginner, Intermediate, and Advanced. System instructions adapt terminology, detail, and complexity.
- **💬 Query Interface:** Interactive coding chatbot with full conversational memory and one-click chat reset.
- **⚡ AI Code Generator:** Generates clean Python/JavaScript, creates real-time Graphviz execution flowcharts, displays interactive keyword tooltips, and supports continuous refinement chat.
- **📖 Code Explainer:** Provides line-by-line breakdowns or simplified beginner explanations alongside original code, with follow-up clarification chat.
- **🐞 Error Detector & Fixer:** 4-tier diagnostic pipeline (Syntax check, Pyflakes linting, Runtime execution check, and Logical review) with minimal-diff fix suggestions and debugging discussion chat.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd coding_tutor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Note: Graphviz also requires the Graphviz system binary installed on your machine if rendering flowcharts locally).*

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and add your Groq API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Run the Application
```bash
streamlit run app.py
```
