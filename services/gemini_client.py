"""
services/gemini_client.py
=========================
Wraps Google Gemini 1.5 Flash API.
Provides 4 prompt templates and generates all narrative formats.
Free tier: 15 RPM, 1,500 RPD — sufficient for this app.
"""

import time
import config

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ── Prompt Templates ───────────────────────────────────────────────────────────
PROMPTS = {
    "release": """You are a technical writer. Based ONLY on the commit data below, write professional Release Notes in Markdown.

Format:
- Group by week/sprint with `## Week of ...` headings
- Use bullet points: `- **[Type]** Short, clear description`
- Include a `### 🏷️ Milestones` section if any version tags exist
- End with a `### 📊 Summary` with commit counts by type
- Do NOT invent features not mentioned in commits
- Be concise and professional

---START_COMMIT_DATA---
{commit_data}
---END_COMMIT_DATA---

Output only the Markdown release notes. Start with `# Release Notes`.
""",

    "standup": """You are a team lead writing a weekly standup report. Based ONLY on the commit data below, write a clear standup summary.

Format:
- One paragraph per week: "This week the team..." 
- Mention key features shipped, bugs fixed, and any milestones
- Use active voice and team-friendly language
- Keep each weekly paragraph to 3-5 sentences
- Do NOT invent work not shown in commits

---START_COMMIT_DATA---
{commit_data}
---END_COMMIT_DATA---

Output only the standup summary in Markdown. Start with `# Standup Summary`.
""",

    "onboarding": """You are a senior engineer writing an onboarding guide for a new team member. Based ONLY on the commit history below, tell the story of how this project evolved.

Format:
- Start with an introduction paragraph about the project
- Tell the story chronologically: "The project started with...", "In the following weeks...", "A major milestone was reached when..."
- Explain what each major phase accomplished
- Highlight key architectural decisions visible from commits
- End with a "Current State" paragraph
- Be welcoming and educational

---START_COMMIT_DATA---
{commit_data}
---END_COMMIT_DATA---

Output only the onboarding story in Markdown. Start with `# Project History & Onboarding Guide`.
""",

    "portfolio": """You are a developer writing a professional portfolio README for this project. Based ONLY on the commit data below, write a compelling project description.

Format:
- `# Project Name` heading (infer from commit context)
- A 2-3 sentence project description
- `## ✨ Features` — bullet list of key features implemented (from feature commits)
- `## 🛠️ Tech Signals` — infer technologies from commit messages
- `## 📈 Development Stats` — commit counts, active weeks, milestones
- `## 🏗️ Development Journey` — brief narrative of how it was built
- Professional, impressive tone suitable for a portfolio

---START_COMMIT_DATA---
{commit_data}
---END_COMMIT_DATA---

Output only the portfolio README in Markdown. Start with `# ` followed by the project name.
""",
}

DEMO_OUTPUTS = {
    "release": """# Release Notes

> ⚠️ **Demo Mode** — Add your Gemini API key in `config.py` for real AI output.

## Week of Apr 01, 2024 (3 commits)

- **[Feature]** Added user authentication with JWT tokens
- **[Feature]** Implemented dashboard homepage
- **[Bug Fix]** Fixed login redirect loop on mobile browsers

### 📊 Summary
| Type | Count |
|------|-------|
| Feature | 2 |
| Bug Fix | 1 |
""",
    "standup": """# Standup Summary

> ⚠️ **Demo Mode** — Add your Gemini API key in `config.py` for real AI output.

This week the team made significant progress. We shipped the user authentication system including JWT token support, and built out the main dashboard. We also resolved a critical bug affecting mobile users where the login page was caught in a redirect loop.

""",
    "onboarding": """# Project History & Onboarding Guide

> ⚠️ **Demo Mode** — Add your Gemini API key in `config.py` for real AI output.

Welcome to the team! This guide will walk you through the history of this project based on its commit history.

The project began with foundational scaffolding and setup. Over the following weeks, the team built out core features including authentication, the main UI, and key business logic. The codebase has evolved through multiple rounds of bug fixing and refinement.

**Current State**: The project is actively developed with regular commits across features, bug fixes, and maintenance tasks.
""",
    "portfolio": """# My Project

> ⚠️ **Demo Mode** — Add your Gemini API key in `config.py` for real AI output.

A full-stack web application built from the ground up with modern development practices.

## ✨ Features
- User authentication and authorization
- Interactive dashboard with real-time data
- Mobile-responsive design

## 📈 Development Stats
- Multiple active development weeks
- Commits across features, bug fixes, and infrastructure

## 🏗️ Development Journey
This project was built iteratively, starting with core infrastructure and progressively adding features based on user feedback.
""",
}


class GeminiClient:
    def __init__(self):
        self._configured = False
        if not GEMINI_AVAILABLE:
            return
        key = config.GEMINI_API_KEY
        if key and key != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=key)
            self._model = genai.GenerativeModel(config.GEMINI_MODEL)
            self._configured = True

    def is_available(self) -> bool:
        return GEMINI_AVAILABLE and self._configured

    def generate_all(self, commit_data_text: str, repo_name: str = "") -> dict:
        """Generate all 4 narrative formats. Returns dict keyed by format name."""
        if not self.is_available():
            return DEMO_OUTPUTS.copy()

        results = {}
        formats = ["release", "standup", "onboarding", "portfolio"]

        for i, fmt in enumerate(formats):
            try:
                results[fmt] = self._generate_single(fmt, commit_data_text)
                # Respect free tier rate limit (15 RPM)
                if i < len(formats) - 1:
                    time.sleep(4)
            except Exception as e:
                results[fmt] = f"*Error generating {fmt}: {str(e)}*\n\n{DEMO_OUTPUTS.get(fmt, '')}"

        return results

    def generate_single(self, fmt: str, commit_data_text: str) -> str:
        """Generate one narrative format."""
        if not self.is_available():
            return DEMO_OUTPUTS.get(fmt, "Demo output not available.")
        return self._generate_single(fmt, commit_data_text)

    def _generate_single(self, fmt: str, commit_data_text: str) -> str:
        prompt_template = PROMPTS.get(fmt, PROMPTS["release"])
        prompt = prompt_template.format(commit_data=commit_data_text)

        generation_config = genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=2048,
        )

        response = self._model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        text = response.text.strip()
        # Strip any preamble before the first # heading
        if "---END_COMMIT_DATA---" in text:
            text = text.split("---END_COMMIT_DATA---")[-1].strip()
        return text


# Singleton instance
gemini = GeminiClient()
