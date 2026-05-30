from flask import Flask, request
from telegram import Bot
import requests
import sqlite3
import os
import json
from io import BytesIO

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

bot = Bot(token=BOT_TOKEN)

DB_NAME = "history.db"

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id TEXT PRIMARY KEY,
        style TEXT DEFAULT 'tech'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        prompt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- STYLES ----------------

def load_styles():

    try:
        with open("styles.json","r") as f:
            return json.load(f)
    except:
        return {}

# ---------------- USER STYLE ----------------

def get_user_style(user_id):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute(
        "SELECT style FROM users WHERE user_id=?",
        (str(user_id),)
    )

    row = cur.fetchone()

    conn.close()

    if row:
        return row[0]

    return "tech"

def set_user_style(user_id, style):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    INSERT OR REPLACE INTO users
    (user_id, style)
    VALUES (?,?)
    """,(str(user_id), style))

    conn.commit()
    conn.close()

# ---------------- HISTORY ----------------

def save_history(user_id, prompt):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    INSERT INTO history(user_id,prompt)
    VALUES (?,?)
    """,(str(user_id), prompt))

    conn.commit()
    conn.close()

def get_history(user_id):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute("""
    SELECT prompt
    FROM history
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 10
    """,(str(user_id),))

    rows = cur.fetchall()

    conn.close()

    return rows
