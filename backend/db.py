import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "news_history.db")

def get_db_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            word_count INTEGER DEFAULT 0,
            char_count INTEGER DEFAULT 0,
            stopword_count INTEGER DEFAULT 0,
            unique_words INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print(f"[Database] SQLite DB initialized at: {DB_PATH}")

def save_prediction(text, prediction, confidence, stats=None):
    """
    Saves prediction result to SQLite database.
    Returns inserted record ID.
    """
    if stats is None:
        stats = {}

    word_count = stats.get("word_count", len(text.split()))
    char_count = stats.get("char_count", len(text))
    stopword_count = stats.get("stopword_count", 0)
    unique_words = stats.get("unique_words", 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (text, prediction, confidence, word_count, char_count, stopword_count, unique_words)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (text, prediction, float(confidence), word_count, char_count, stopword_count, unique_words))
    
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_history(limit=100, search_query=None):
    """
    Retrieves prediction history sorted by most recent first.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if search_query and search_query.strip():
        like_pattern = f"%{search_query.strip()}%"
        cursor.execute("""
            SELECT id, text, prediction, confidence, word_count, char_count, stopword_count, unique_words, created_at
            FROM predictions
            WHERE text LIKE ? OR prediction LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (like_pattern, like_pattern, limit))
    else:
        cursor.execute("""
            SELECT id, text, prediction, confidence, word_count, char_count, stopword_count, unique_words, created_at
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "id": r["id"],
            "text": r["text"],
            "prediction": r["prediction"],
            "confidence": round(r["confidence"], 1),
            "word_count": r["word_count"],
            "char_count": r["char_count"],
            "stopword_count": r["stopword_count"],
            "unique_words": r["unique_words"],
            "created_at": r["created_at"]
        })
    return history

def get_analytics():
    """
    Computes summary metrics for analytics dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM predictions")
    total = cursor.fetchone()["total"]

    if total == 0:
        conn.close()
        return {
            "total_analyzed": 0,
            "real_count": 0,
            "fake_count": 0,
            "real_percentage": 0.0,
            "fake_percentage": 0.0,
            "avg_confidence": 0.0,
            "avg_word_count": 0.0
        }

    cursor.execute("SELECT COUNT(*) as real_cnt FROM predictions WHERE UPPER(prediction) = 'REAL'")
    real_cnt = cursor.fetchone()["real_cnt"]

    cursor.execute("SELECT COUNT(*) as fake_cnt FROM predictions WHERE UPPER(prediction) = 'FAKE'")
    fake_cnt = cursor.fetchone()["fake_cnt"]

    cursor.execute("SELECT AVG(confidence) as avg_conf FROM predictions")
    avg_conf = cursor.fetchone()["avg_conf"] or 0.0

    cursor.execute("SELECT AVG(word_count) as avg_words FROM predictions")
    avg_words = cursor.fetchone()["avg_words"] or 0.0

    conn.close()

    return {
        "total_analyzed": total,
        "real_count": real_cnt,
        "fake_count": fake_cnt,
        "real_percentage": round((real_cnt / total) * 100, 1),
        "fake_percentage": round((fake_cnt / total) * 100, 1),
        "avg_confidence": round(avg_conf, 1),
        "avg_word_count": round(avg_words, 1)
    }

def delete_prediction(record_id):
    """Deletes a single prediction record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_history():
    """Deletes all prediction records from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
