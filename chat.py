"""
chat.py - OpenRouter API + DuckDuckGo search
Silently searches, then sends context to AI, returns only final reply
"""

import os
import sys
import io
import requests
import warnings
import logging
from dotenv import load_dotenv
import search as search_module
import database as db

# Suppress all ddgs warnings globally
warnings.filterwarnings("ignore")
logging.getLogger("ddgs").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
API_URL            = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are BRO — a smart, friendly, and concise AI assistant in a terminal CLI.
You have been given real-time web search results as context. Use them to answer accurately.
Always cite key facts from the search context. Keep answers clear and well-formatted for a terminal.
If the search results are not relevant, use your own knowledge but mention it."""


def ask(user_query: str, email: str, console=None) -> str:
    """
    1. Silently search DuckDuckGo for context (no output to user)
    2. Send query + context to OpenRouter
    3. Save to history
    4. Return only the final AI reply
    """

    # ── Silent search - capture ALL output/warnings ───────────────────────────
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    sys.stderr = io.StringIO()

    try:
        context = search_module.search_web(user_query)
    except Exception:
        context = ""
    finally:
        sys.stderr = old_stderr

    # ── Build messages ────────────────────────────────────────────────────────
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Last 10 history turns for continuity
    history = db.get_history(email)[-10:]
    for h in history:
        if h["role"] in ("user", "assistant"):
            messages.append({"role": h["role"], "content": h["content"]})

    # User message with search context
    user_content = f"User Question: {user_query}"
    if context:
        user_content += f"\n\n--- Web Search Context ---\n{context}\n--- End Context ---"

    messages.append({"role": "user", "content": user_content})

    # Save user query to history
    db.save_history(email, "user", user_query)

    # ── Call OpenRouter ───────────────────────────────────────────────────────
    try:
        resp = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://bro-cli.local",
                "X-Title":       "BRO CLI"
            },
            json={
                "model":       OPENROUTER_MODEL,
                "messages":    messages,
                "max_tokens":  1024,
                "temperature": 0.7
            },
            timeout=30
        )
        resp.raise_for_status()
        data  = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        reply = "Request timed out. Please try again."
    except Exception as e:
        reply = f"API Error: {e}"

    # Save reply to history
    db.save_history(email, "assistant", reply)
    return reply