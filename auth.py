"""
auth.py - Registration, login, email verification
Restored to original working version (Feb 24)
"""

import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import database as db

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip().replace(" ", "")


def send_verification_email(to_email: str, code: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "BRO CLI - Your Verification Code"
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email

        # plain text only - no HTML, no f-string curly brace issues
        plain = (
            "BRO CLI - Email Verification\n\n"
            "Your one-time verification code is:\n\n"
            f"     {code}\n\n"
            "This code is valid for 10 minutes.\n"
            "If you did not request this, ignore this email.\n\n"
            "- The BRO CLI Team"
        )
        msg.attach(MIMEText(plain, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        return True, ""

    except smtplib.SMTPAuthenticationError as e:
        return False, f"Auth failed: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def register_flow(console, theme) -> dict | None:
    from rich.prompt import Prompt

    console.print(f"\n[bold {theme}]  +- NEW ACCOUNT REGISTRATION -+[/]")

    username = Prompt.ask(f"  [bold {theme}]Username[/]").strip()
    if not username:
        console.print("[red]  x Username cannot be empty.[/]")
        return None

    email = Prompt.ask(f"  [bold {theme}]Email[/]").strip()
    if not email or "@" not in email:
        console.print("[red]  x Invalid email address.[/]")
        return None

    if db.user_exists(email):
        console.print("[red]  x Account with this email already exists.[/]")
        return None

    password = Prompt.ask(f"  [bold {theme}]Password[/]", password=True).strip()
    if len(password) < 6:
        console.print("[red]  x Password must be at least 6 characters.[/]")
        return None

    confirm = Prompt.ask(f"  [bold {theme}]Confirm Password[/]", password=True).strip()
    if password != confirm:
        console.print("[red]  x Passwords do not match.[/]")
        return None

    db.create_user(username, email, password)

    otp = generate_otp()
    console.print(f"\n  [yellow]Sending verification code to {email}...[/]")
    sent, error = send_verification_email(email, otp)

    if not sent:
        console.print(f"[red]  x Failed to send email: {error}[/]")
        db.delete_user(email)
        console.print(f"[yellow]  Try registering again.[/]")
        return None

    console.print(f"  [green]✓ Code sent to {email} — check your inbox![/]")

    for attempt in range(3):
        entered = Prompt.ask(f"  [bold {theme}]Enter 6-digit OTP[/]").strip()
        if entered == otp:
            db.verify_user(email)
            console.print(f"  [bold green]✓ Email verified! Welcome, {username}![/]\n")
            return db.check_login(email, password)
        else:
            remaining = 2 - attempt
            if remaining:
                console.print(f"  [red]x Wrong OTP. {remaining} attempt(s) left.[/]")
            else:
                console.print("  [red]x Too many wrong attempts.[/]")
                db.delete_user(email)
                return None


def login_flow(console, theme) -> dict | None:
    from rich.prompt import Prompt

    console.print(f"\n[bold {theme}]  +- LOGIN -+[/]")

    email    = Prompt.ask(f"  [bold {theme}]Email[/]").strip()
    password = Prompt.ask(f"  [bold {theme}]Password[/]", password=True).strip()

    if db.user_exists(email) and db.is_banned(email):
        console.print("  [bold red]x Your account has been banned. Contact admin.[/]")
        return None

    meta = db.check_login(email, password)
    if not meta:
        console.print("  [red]x Invalid email or password.[/]")
        return None

    if meta.get("verified") != "true":
        console.print("  [red]x Account not verified. Please register again.[/]")
        return None

    console.print(f"  [bold green]✓ Welcome back, {meta['username']}![/]\n")
    return meta