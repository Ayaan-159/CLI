"""
admin.py - Admin panel for BRO CLI
Features:
  - View all registered users
  - Delete any user account
  - View full search history of any user
  - Clear history of any user
  - Ban / unban users
  - Live stats (total users, total messages)
"""

from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich.prompt  import Prompt
import database as db

console = Console()

ADMIN_EMAIL    = "admin"
ADMIN_PASSWORD = "admin123"   # Change this to your own secure password!


def admin_login(theme: str) -> bool:
    """Simple admin login. Returns True if credentials match."""
    console.print(f"\n[bold {theme}]  ┌─ ADMIN LOGIN ─┐[/]")
    email = Prompt.ask(f"  [bold {theme}]Admin Username[/]").strip()
    pw    = Prompt.ask(f"  [bold {theme}]Admin Password[/]", password=True).strip()
    if email == ADMIN_EMAIL and pw == ADMIN_PASSWORD:
        console.print(f"  [bold green]✓ Admin access granted![/]\n")
        return True
    console.print("  [red]✗ Wrong admin credentials.[/]")
    return False


def show_stats(theme: str):
    """Show total users and total messages."""
    users   = db.get_all_users()
    all_h   = db.get_all_history()
    total_u = len(users)
    total_m = len(all_h)

    panel = Panel(
        f"[bold {theme}]Total Users   :[/]  {total_u}\n"
        f"[bold {theme}]Total Messages:[/]  {total_m}",
        title=f"[bold {theme}]📊 BRO CLI Stats[/]",
        border_style=theme,
        padding=(1, 4)
    )
    console.print(panel)


def show_all_users(theme: str):
    """Display all registered users in a table."""
    users = db.get_all_users()
    if not users:
        console.print("  [dim]No users registered yet.[/dim]")
        return

    table = Table(title="All Users", border_style=theme, show_lines=True)
    table.add_column("Username",   style=f"bold {theme}", width=15)
    table.add_column("Email",      width=30)
    table.add_column("Verified",   width=10)
    table.add_column("Banned",     width=10)
    table.add_column("Created At", width=22)

    for u in users:
        verified = "[green]Yes[/]" if u.get("verified") == "true"  else "[red]No[/]"
        banned   = "[red]Yes[/]"   if u.get("banned")   == "true"  else "[green]No[/]"
        table.add_row(
            u.get("username", ""),
            u.get("email", ""),
            verified,
            banned,
            u.get("created_at", "")[:19].replace("T", " ")
        )
    console.print(table)


def view_user_history(theme: str):
    """View full search/chat history of a specific user."""
    email = Prompt.ask(f"  [bold {theme}]Enter user email[/]").strip()
    if not db.user_exists(email):
        console.print("  [red]✗ User not found.[/]")
        return

    history = db.get_history(email)
    if not history:
        console.print(f"  [dim]No history found for {email}.[/dim]")
        return

    table = Table(title=f"History: {email}", border_style=theme, show_lines=True)
    table.add_column("Time",    style="dim",           width=20)
    table.add_column("Role",    style=f"bold {theme}", width=10)
    table.add_column("Message", overflow="fold")

    for entry in history:
        ts   = entry["timestamp"][:19].replace("T", " ")
        role = entry["role"].capitalize()
        msg  = entry["content"][:300] + ("..." if len(entry["content"]) > 300 else "")
        table.add_row(ts, role, msg)

    console.print(table)
    console.print(f"  [dim]Total: {len(history)} messages[/dim]")


def delete_user(theme: str):
    """Delete a user account and all their history."""
    show_all_users(theme)
    email = Prompt.ask(f"\n  [bold {theme}]Enter email to DELETE[/]").strip()

    if not db.user_exists(email):
        console.print("  [red]✗ User not found.[/]")
        return

    confirm = Prompt.ask(
        f"  [bold red]Are you sure you want to delete {email}? (yes/no)[/]"
    ).strip().lower()

    if confirm == "yes":
        db.delete_user(email)
        console.print(f"  [green]✓ User {email} and all their data deleted.[/]")
    else:
        console.print("  [yellow]Cancelled.[/]")


def clear_user_history(theme: str):
    """Clear history of a specific user."""
    email = Prompt.ask(f"  [bold {theme}]Enter user email to clear history[/]").strip()
    if not db.user_exists(email):
        console.print("  [red]✗ User not found.[/]")
        return
    count = db.clean_history(email)
    console.print(f"  [green]✓ Cleared {count} history entries for {email}.[/]")


def ban_user(theme: str):
    """Ban a user — they won't be able to login."""
    email = Prompt.ask(f"  [bold {theme}]Enter email to BAN[/]").strip()
    if not db.user_exists(email):
        console.print("  [red]✗ User not found.[/]")
        return
    db.set_ban(email, True)
    console.print(f"  [red]✓ User {email} has been BANNED.[/]")


def unban_user(theme: str):
    """Unban a user."""
    email = Prompt.ask(f"  [bold {theme}]Enter email to UNBAN[/]").strip()
    if not db.user_exists(email):
        console.print("  [red]✗ User not found.[/]")
        return
    db.set_ban(email, False)
    console.print(f"  [green]✓ User {email} has been UNBANNED.[/]")


def admin_panel(theme: str):
    """Main admin panel loop."""
    if not admin_login(theme):
        return

    while True:
        console.print(f"\n[bold {theme}]  ╔══════════════════════════╗[/]")
        console.print(f"[bold {theme}]  ║      ADMIN PANEL         ║[/]")
        console.print(f"[bold {theme}]  ╚══════════════════════════╝[/]")
        console.print(f"  [bold {theme}][1][/] View all users")
        console.print(f"  [bold {theme}][2][/] View user history")
        console.print(f"  [bold {theme}][3][/] Delete user")
        console.print(f"  [bold {theme}][4][/] Clear user history")
        console.print(f"  [bold {theme}][5][/] Ban user")
        console.print(f"  [bold {theme}][6][/] Unban user")
        console.print(f"  [bold {theme}][7][/] Stats")
        console.print(f"  [bold {theme}][8][/] Exit admin panel\n")

        choice = Prompt.ask(
            f"  [bold {theme}]Admin choice[/]",
            choices=["1","2","3","4","5","6","7","8"],
            default="8"
        )

        if   choice == "1": show_all_users(theme)
        elif choice == "2": view_user_history(theme)
        elif choice == "3": delete_user(theme)
        elif choice == "4": clear_user_history(theme)
        elif choice == "5": ban_user(theme)
        elif choice == "6": unban_user(theme)
        elif choice == "7": show_stats(theme)
        elif choice == "8":
            console.print(f"  [bold {theme}]Exiting admin panel.[/]\n")
            break