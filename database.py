"""
database.py - ChromaDB connection, saving/loading chat history and users
"""

import chromadb
import hashlib
import uuid
from datetime import datetime

# Initialize ChromaDB client (persistent local storage)
client = chromadb.PersistentClient(path=".bro_db")

# Collections
users_col   = client.get_or_create_collection("users")
history_col = client.get_or_create_collection("chat_history")


# ─── Password ─────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─── User helpers ─────────────────────────────────────────────────────────────

def user_exists(email: str) -> bool:
    results = users_col.get(ids=[email])
    return len(results["ids"]) > 0


def create_user(username: str, email: str, password: str) -> None:
    users_col.add(
        ids=[email],
        documents=[username],
        metadatas=[{
            "username":      username,
            "email":         email,
            "password_hash": hash_password(password),
            "verified":      "false",
            "banned":        "false",
            "created_at":    datetime.now().isoformat()
        }]
    )


def verify_user(email: str) -> None:
    result = users_col.get(ids=[email])
    if result["ids"]:
        meta = result["metadatas"][0]
        meta["verified"] = "true"
        users_col.update(ids=[email], metadatas=[meta])


def is_verified(email: str) -> bool:
    result = users_col.get(ids=[email])
    if result["ids"]:
        return result["metadatas"][0].get("verified") == "true"
    return False


def check_login(email: str, password: str) -> dict | None:
    """Return user metadata if credentials match, else None."""
    result = users_col.get(ids=[email])
    if not result["ids"]:
        return None
    meta = result["metadatas"][0]
    if meta["password_hash"] == hash_password(password):
        return meta
    return None


def get_username(email: str) -> str:
    result = users_col.get(ids=[email])
    if result["ids"]:
        return result["metadatas"][0].get("username", "User")
    return "User"


def get_all_users() -> list[dict]:
    """Return list of all user metadata dicts."""
    results = users_col.get()
    if not results["ids"]:
        return []
    return results["metadatas"]


def delete_user(email: str) -> None:
    """Delete user account and all their history."""
    if user_exists(email):
        users_col.delete(ids=[email])
    clean_history(email)


def set_ban(email: str, banned: bool) -> None:
    """Ban or unban a user."""
    result = users_col.get(ids=[email])
    if result["ids"]:
        meta = result["metadatas"][0]
        meta["banned"] = "true" if banned else "false"
        users_col.update(ids=[email], metadatas=[meta])


def is_banned(email: str) -> bool:
    result = users_col.get(ids=[email])
    if result["ids"]:
        return result["metadatas"][0].get("banned") == "true"
    return False


# ─── History helpers ───────────────────────────────────────────────────────────

def save_history(email: str, role: str, content: str) -> None:
    entry_id = str(uuid.uuid4())
    history_col.add(
        ids=[entry_id],
        documents=[content],
        metadatas=[{
            "email":     email,
            "role":      role,
            "timestamp": datetime.now().isoformat()
        }]
    )


def get_history(email: str) -> list[dict]:
    """Retrieve all history for a user, sorted by timestamp."""
    results = history_col.get(where={"email": email})
    if not results["ids"]:
        return []
    entries = []
    for doc, meta in zip(results["documents"], results["metadatas"]):
        entries.append({
            "role":      meta["role"],
            "content":   doc,
            "timestamp": meta["timestamp"]
        })
    entries.sort(key=lambda x: x["timestamp"])
    return entries


def get_all_history() -> list[dict]:
    """Retrieve ALL history from ALL users (admin use)."""
    results = history_col.get()
    if not results["ids"]:
        return []
    entries = []
    for doc, meta in zip(results["documents"], results["metadatas"]):
        entries.append({
            "email":     meta.get("email", ""),
            "role":      meta.get("role", ""),
            "content":   doc,
            "timestamp": meta.get("timestamp", "")
        })
    return entries


def clean_history(email: str) -> int:
    """Delete all history entries for a user. Returns count deleted."""
    results = history_col.get(where={"email": email})
    ids = results["ids"]
    if ids:
        history_col.delete(ids=ids)
    return len(ids)