import sqlite3
from datetime import datetime, timezone, timedelta
from config import DB_PATH

UZB_TZ = timezone(timedelta(hours=5))

def get_now():
    return datetime.now(UZB_TZ).strftime("%Y-%m-%d %H:%M:%S")

def _get_connection():
    return sqlite3.connect(str(DB_PATH))

def _init_db_sync():
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT,
                last_active TEXT,
                is_blocked INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                username TEXT,
                added_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                sent_count INTEGER,
                failed_count INTEGER,
                target_type TEXT DEFAULT 'users',
                created_at TEXT
            )
        """)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(broadcasts)")
        cols = [c[1] for c in cur.fetchall()]
        if "target_type" not in cols:
            conn.execute("ALTER TABLE broadcasts ADD COLUMN target_type TEXT DEFAULT 'users'")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                created_at TEXT
            )
        """)
        conn.commit()

async def init_db():
    _init_db_sync()

def _add_or_update_user_sync(user_id: int, username: str | None, full_name: str | None):
    now = get_now()
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO users (user_id, username, full_name, joined_at, last_active, is_blocked)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                last_active = excluded.last_active,
                is_blocked = 0
        """, (user_id, username or "", full_name or "", now, now))
        conn.commit()

async def add_or_update_user(user_id: int, username: str | None, full_name: str | None):
    _add_or_update_user_sync(user_id, username, full_name)

def _mark_user_blocked_sync(user_id: int):
    with _get_connection() as conn:
        conn.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

async def mark_user_blocked(user_id: int):
    _mark_user_blocked_sync(user_id)

def _get_user_stats_sync():
    now_date = datetime.now(UZB_TZ).strftime("%Y-%m-%d")
    week_ago = (datetime.now(UZB_TZ) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE joined_at LIKE ?", (f"{now_date}%",))
        today_joined = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (week_ago,))
        weekly_active = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        blocked = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM groups WHERE is_active = 1")
        group_count = cur.fetchone()[0]

    return {
        "total": total,
        "today_joined": today_joined,
        "weekly_active": weekly_active,
        "blocked": blocked,
        "active_total": max(0, total - blocked),
        "group_count": group_count
    }

async def get_user_stats():
    return _get_user_stats_sync()

def _get_all_active_users_sync():
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE is_blocked = 0")
        rows = cur.fetchall()
        return [r[0] for r in rows]

async def get_all_active_users():
    return _get_all_active_users_sync()

def _get_recent_users_sync(limit: int = 15):
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, full_name, joined_at, last_active, is_blocked
            FROM users
            ORDER BY last_active DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        users = []
        for r in rows:
            users.append({
                "user_id": r[0],
                "username": r[1],
                "full_name": r[2],
                "joined_at": r[3],
                "last_active": r[4],
                "is_blocked": bool(r[5])
            })
        return users

async def get_recent_users(limit: int = 15):
    return _get_recent_users_sync(limit)

def _get_all_users_export_sync():
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, full_name, joined_at, last_active, is_blocked
            FROM users
            ORDER BY joined_at DESC
        """)
        return cur.fetchall()

async def get_all_users_export():
    return _get_all_users_export_sync()

# ==================== GROUP MANAGEMENT ====================
def _add_or_update_group_sync(chat_id: int, title: str, username: str | None):
    now = get_now()
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO groups (chat_id, title, username, added_at, is_active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(chat_id) DO UPDATE SET
                title = excluded.title,
                username = excluded.username,
                is_active = 1
        """, (chat_id, title or "Nomsiz guruh", username or "", now))
        conn.commit()

async def add_or_update_group(chat_id: int, title: str, username: str | None):
    _add_or_update_group_sync(chat_id, title, username)

def _remove_group_sync(chat_id: int):
    with _get_connection() as conn:
        conn.execute("UPDATE groups SET is_active = 0 WHERE chat_id = ?", (chat_id,))
        conn.commit()

async def remove_group(chat_id: int):
    _remove_group_sync(chat_id)

def _get_all_active_groups_sync():
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT chat_id, title, username, added_at FROM groups WHERE is_active = 1")
        rows = cur.fetchall()
        groups = []
        for r in rows:
            groups.append({
                "chat_id": r[0],
                "title": r[1],
                "username": r[2],
                "added_at": r[3]
            })
        return groups

async def get_all_active_groups():
    return _get_all_active_groups_sync()

# ==================== SETTINGS & LOGS ====================
def _get_setting_sync(key: str, default: str) -> str:
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            return row[0]
        return default

async def get_setting(key: str, default: str = "") -> str:
    return _get_setting_sync(key, default)

def _set_setting_sync(key: str, value: str):
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()

async def set_setting(key: str, value: str):
    _set_setting_sync(key, value)

def _log_broadcast_sync(admin_id: int, sent_count: int, failed_count: int, target_type: str = "users"):
    now = get_now()
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO broadcasts (admin_id, sent_count, failed_count, target_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, sent_count, failed_count, target_type, now))
        conn.commit()

async def log_broadcast(admin_id: int, sent_count: int, failed_count: int, target_type: str = "users"):
    _log_broadcast_sync(admin_id, sent_count, failed_count, target_type)

def _save_feedback_sync(user_id: int, message: str):
    now = get_now()
    with _get_connection() as conn:
        conn.execute("""
            INSERT INTO feedbacks (user_id, message, created_at)
            VALUES (?, ?, ?)
        """, (user_id, message, now))
        conn.commit()

async def save_feedback(user_id: int, message: str):
    _save_feedback_sync(user_id, message)
