import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "support.db")


# -----------------------------
# Connection
# -----------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Setup
# -----------------------------

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            action TEXT NOT NULL,
            answer TEXT,
            source TEXT,
            confidence_score TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            route TEXT NOT NULL,
            rating TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            city TEXT,
            country TEXT,
            registered_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Chat history
# -----------------------------

def insert_chat(question, action, answer="", source="", confidence_score=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (timestamp, question, action, answer, source, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), question, action, answer, source, str(confidence_score)))
    conn.commit()
    conn.close()


def get_chat_history(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_history
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_chat_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT action, COUNT(*) as count
        FROM chat_history
        GROUP BY action
    """)
    rows = {row["action"]: row["count"] for row in cursor.fetchall()}
    conn.close()
    return rows


# -----------------------------
# Escalations
# -----------------------------

def insert_escalation(question, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO escalations (timestamp, question, reason)
        VALUES (?, ?, ?)
    """, (datetime.now().isoformat(), question, reason))
    conn.commit()
    conn.close()


def get_escalations(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM escalations
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# -----------------------------
# Feedback
# -----------------------------

def insert_feedback(question, route, rating):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (timestamp, question, route, rating)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), question, route, rating))
    conn.commit()
    conn.close()


def get_feedback(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM feedback
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_feedback_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rating, COUNT(*) as count
        FROM feedback
        GROUP BY rating
    """)
    rows = {row["rating"]: row["count"] for row in cursor.fetchall()}
    conn.close()
    return {
        "thumbs_up": rows.get("thumbs_up", 0),
        "thumbs_down": rows.get("thumbs_down", 0),
    }


# -----------------------------
# Customers
# -----------------------------

def insert_customer(customer_name, email, phone="", city="", country=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO customers (customer_name, email, phone, city, country, registered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_name, email, phone, city, country, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def get_customers(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM customers
        ORDER BY registered_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def seed_customers():
    sample_customers = [
        ("Alice Brown", "alice.brown@email.com", "+44 7700 900001", "London", "UK"),
        ("James Smith", "james.smith@email.com", "+44 7700 900002", "Manchester", "UK"),
        ("Sara Khan", "sara.khan@email.com", "+44 7700 900003", "Birmingham", "UK"),
        ("Daniel Lee", "daniel.lee@email.com", "+1 555 000 0001", "New York", "USA"),
        ("Emma Wilson", "emma.wilson@email.com", "+1 555 000 0002", "Los Angeles", "USA"),
        ("Liam Johnson", "liam.johnson@email.com", "+1 555 000 0003", "Chicago", "USA"),
        ("Olivia Davis", "olivia.davis@email.com", "+49 30 000001", "Berlin", "Germany"),
        ("Noah Martinez", "noah.martinez@email.com", "+34 91 000001", "Madrid", "Spain"),
        ("Ava Thompson", "ava.thompson@email.com", "+33 1 00000001", "Paris", "France"),
        ("William Garcia", "william.garcia@email.com", "+1 555 000 0004", "Houston", "USA"),
        ("Sophia Anderson", "sophia.anderson@email.com", "+44 7700 900004", "Leeds", "UK"),
        ("James Taylor", "james.taylor@email.com", "+44 7700 900005", "Glasgow", "UK"),
        ("Isabella White", "isabella.white@email.com", "+1 555 000 0005", "Phoenix", "USA"),
        ("Benjamin Harris", "benjamin.harris@email.com", "+61 2 0000001", "Sydney", "Australia"),
        ("Mia Clark", "mia.clark@email.com", "+61 3 0000001", "Melbourne", "Australia"),
    ]
    for customer in sample_customers:
        insert_customer(*customer)