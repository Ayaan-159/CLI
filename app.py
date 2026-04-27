"""
app.py - BRO CLI Main Loop
Features:
  - Splash screen with ASCII art in a frame
  - User registration / login with email OTP
  - Admin panel with full user control
  - DuckDuckGo search -> AI reply via OpenRouter
  - '+' prefix  -> autocomplete files in current directory
  - '/'  prefix -> open OS file explorer, then attach path
  - /logout     -> logout
  - /h          -> show search history
  - /clean      -> clear history
  - Blue theme fixed, answer box always red with white text
"""

import os
import sys
import glob
import tkinter as tk
from tkinter import filedialog

from rich.console import Console
from rich.panel   import Panel
from rich.text    import Text
from rich.prompt  import Prompt
from rich.table   import Table
from prompt_toolkit                  import PromptSession
from prompt_toolkit.completion       import Completer, Completion
from prompt_toolkit.key_binding      import KeyBindings
from prompt_toolkit.formatted_text   import HTML

import auth
import database as db
import chat as chat_module
import admin as admin_module

# ─── Reply formatter: **bold**, links in blue ─────────────────────────────────
import re

def format_reply(text: str):
    """
    Convert markdown-style **bold** and URLs into a Rich Text object.
    - **text** -> bold white
    - http/https URLs -> bold blue underline (clickable in some terminals)
    """
    from rich.text import Text as RText
    result = RText()

    # Regex: match **bold**, URLs, or plain text segments
    pattern = re.compile(
        r"(\*\*(.+?)\*\*)"          # **bold**
        r"|(https?://[^\s\)\]]+)"   # URLs
        r"|([^*h]+|[*h])"           # everything else
    )

    i = 0
    while i < len(text):
        # Check for **bold**
        m_bold = re.match(r"\*\*(.+?)\*\*", text[i:])
        if m_bold:
            result.append(m_bold.group(1), style="bold white")
            i += len(m_bold.group(0))
            continue

        # Check for URL
        m_url = re.match(r"https?://[^\s\)\]]+", text[i:])
        if m_url:
            url = m_url.group(0)
            result.append(url, style="bold blue underline")
            i += len(url)
            continue

        # Plain character
        result.append(text[i], style="white")
        i += 1

    return result


# ─── Theme cycle ──────────────────────────────────────────────────────────────
# Theme is fixed to blue
THEME = "blue"

def current_theme() -> str:
    return THEME

# ─── Console ──────────────────────────────────────────────────────────────────
console = Console()

# ─── ASCII Art ────────────────────────────────────────────────────────────────
BRO_ART = r"""
██████╗ ██████╗  ██████╗ 
██╔══██╗██╔══██╗██╔═══██╗
██████╔╝██████╔╝██║   ██║
██╔══██╗██╔══██╝██║   ██║
██████╔╝██║  ██║╚██████╔╝
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
""".strip()

VERSION = "v1.1.0"


def show_splash():
    theme   = current_theme()
    art     = Text(BRO_ART, style=f"bold {theme}")
    ver     = Text(f"\n  {VERSION}  -  AI-Powered CLI Bot with Web Search", style=f"dim {theme}")
    content = Text()
    content.append_text(art)
    content.append_text(ver)
    panel = Panel(
        content,
        border_style=theme,
        padding=(1, 4),
        title=f"[bold {theme}]  Welcome bro  [/]",
        title_align="center"
    )
    console.print(panel)
    console.print()


# ─── File completer for '+' prefix ────────────────────────────────────────────
class FileCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text
        if text.startswith("+"):
            prefix  = text[1:]
            matches = glob.glob(f"{prefix}*")
            for m in matches:
                yield Completion(m, start_position=-len(prefix), display=m)


# ─── Open file explorer ───────────────────────────────────────────────────────
def open_file_explorer():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(title="Select a file - BRO CLI")
        root.destroy()
        return path if path else None
    except Exception:
        console.print("  [yellow]GUI picker unavailable. Enter path manually:[/]")
        p = Prompt.ask("  File path").strip()
        return p if p else None


# ─── History display ──────────────────────────────────────────────────────────
def show_history(email: str):
    history = db.get_history(email)
    if not history:
        console.print("  [dim]No history yet.[/dim]")
        return
    theme = current_theme()
    table = Table(title="Chat History", border_style=theme, show_lines=True)
    table.add_column("Time",    style="dim",           width=20)
    table.add_column("Role",    style=f"bold {theme}", width=10)
    table.add_column("Message", overflow="fold")
    for entry in history[-30:]:
        ts   = entry["timestamp"][:19].replace("T", " ")
        role = entry["role"].capitalize()
        msg  = entry["content"][:200] + ("..." if len(entry["content"]) > 200 else "")
        table.add_row(ts, role, msg)
    console.print(table)


# ─── Key bindings (no theme cycling) ─────────────────────────────────────────
bindings = KeyBindings()


# ─── Build prompt session ─────────────────────────────────────────────────────
def make_session() -> PromptSession:
    return PromptSession(
        completer=FileCompleter(),
        key_bindings=bindings,
        complete_while_typing=True,
    )


# ─── Auth / main menu ─────────────────────────────────────────────────────────
def auth_flow() -> dict:
    """Loop until user successfully logs in or registers."""
    while True:
        theme = current_theme()
        console.print(f"\n  [bold {theme}]Choose an option:[/]")
        console.print(f"  [bold {theme}][1][/] Login")
        console.print(f"  [bold {theme}][2][/] Register")
        console.print(f"  [bold {theme}][3][/] Admin Panel")
        console.print(f"  [bold {theme}][4][/] Exit\n")

        choice = Prompt.ask("  Your choice", choices=["1","2","3","4"], default="1")

        if choice == "4":
            console.print(f"\n  [bold {current_theme()}]Goodbye, bro! 👋[/]\n")
            sys.exit(0)

        elif choice == "1":
            meta = auth.login_flow(console, current_theme())
            if meta:
                return meta

        elif choice == "2":
            meta = auth.register_flow(console, current_theme())
            if meta:
                return meta

        elif choice == "3":
            admin_module.admin_panel(current_theme())


# ─── Main chat loop ───────────────────────────────────────────────────────────
def chat_loop(user_meta: dict):
    email    = user_meta["email"]
    username = user_meta["username"]
    session  = make_session()

    theme = current_theme()
    console.print(f"  [bold {theme}]Commands:[/] /logout  /h (history)  /clean  + (file suggest)  / (file picker)\n")

    attached_file = None

    while True:
        theme = current_theme()

        prompt_label = HTML(
            f'<b>  [{username}]</b> > '
        )

        try:
            user_input = session.prompt(prompt_label).strip()
        except (EOFError, KeyboardInterrupt):
            console.print(f"\n  [bold {theme}]Goodbye, bro! 👋[/]\n")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────

        if user_input.lower() == "/logout":
            console.print(f"  [bold {theme}]Logged out. See you later, bro! 👋[/]\n")
            return "logout"

        if user_input.lower() == "/h":
            show_history(email)
            continue

        if user_input.lower() == "/clean":
            count = db.clean_history(email)
            console.print(f"  [green]✓ Cleared {count} history entries.[/]")
            continue

        # ── '/' alone — open file explorer ───────────────────────────────────
        if user_input == "/":
            path = open_file_explorer()
            if path:
                attached_file = path
                console.print(f"  [green]✓ File attached:[/] {path}")
                console.print("  [dim]Now type your question about this file.[/dim]")
            continue

        # ── '+filename' — attach file from autocomplete ───────────────────────
        if user_input.startswith("+"):
            file_path = user_input[1:].strip()
            if os.path.isfile(file_path):
                attached_file = file_path
                console.print(f"  [green]✓ File attached:[/] {file_path}")
                console.print("  [dim]Now type your question about this file.[/dim]")
            else:
                console.print(f"  [red]x File not found: {file_path}[/]")
            continue

        # ── Regular query ──────────────────────────────────────────────────────
        query = user_input
        if attached_file:
            try:
                with open(attached_file, "r", errors="replace") as f:
                    file_content = f.read(4000)
                query = f"{user_input}\n\n[Attached file: {attached_file}]\n{file_content}"
                console.print(f"  [dim]Including content of {attached_file}[/dim]")
            except Exception as e:
                console.print(f"  [red]Could not read file: {e}[/]")
            attached_file = None

        # ── AI Response ───────────────────────────────────────────────────────
        reply = chat_module.ask(query, email, console=None)

        reply_panel = Panel(
            format_reply(reply),
            border_style="red",
            title="[bold red]BRO AI[/]",
            title_align="left",
            padding=(0, 2)
        )
        console.print(reply_panel)
        console.print()

    return "exit"


# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    show_splash()
    while True:
        user_meta = auth_flow()
        result    = chat_loop(user_meta)
        if result == "exit":
            console.print(f"\n  [bold {current_theme()}]Goodbye, bro! 👋[/]\n")
            break


if __name__ == "__main__":
    main()