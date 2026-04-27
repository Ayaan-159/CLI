"""
search.py - DuckDuckGo search integration
Suppresses impersonate warnings, returns clean context
"""

import warnings
import logging

# Suppress the impersonate warning completely
warnings.filterwarnings("ignore")
logging.getLogger("ddgs").setLevel(logging.ERROR)
logging.getLogger("duckduckgo_search").setLevel(logging.ERROR)

from ddgs import DDGS


def search_web(query: str, max_results: int = 5) -> str:
    """
    Search DuckDuckGo and return context string for AI.
    Returns empty string if no results found.
    """
    try:
        import sys
        import io

        # Suppress any stderr warnings during search
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()

        results = []
        try:
            ddgs = DDGS()
            results = list(ddgs.text(
                query,
                max_results=max_results,
                safesearch="moderate"
            ))
        finally:
            sys.stderr = old_stderr  # always restore stderr

        if not results:
            return ""

        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body  = r.get("body", "")
            href  = r.get("href", "")
            context_parts.append(
                f"[Result {i}] {title}\n{body}\nSource: {href}"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        return f"[Search Error: {e}]"