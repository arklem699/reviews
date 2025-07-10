from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)

DATABASE = 'reviews.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def determine_sentiment(text):
    text = text.lower()
    positive_words = ['хорош', 'люблю']
    negative_words = ['плохо', 'ненавиж']
    
    for word in positive_words:
        if word in text:
            return 'positive'
    
    for word in negative_words:
        if word in text:
            return 'negative'
    
    return 'neutral'


@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Text is required'}), 400
    
    text = data['text']
    sentiment = determine_sentiment(text)
    created_at = datetime.utcnow().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
        (text, sentiment, created_at)
    )
    conn.commit()
    
    review_id = cursor.lastrowid
    cursor.execute('SELECT * FROM reviews WHERE id = ?', (review_id,))
    review = dict(cursor.fetchone())
    conn.close()
    
    return jsonify(review), 201


@app.route('/reviews', methods=['GET'])
def get_reviews():
    sentiment_filter = request.args.get('sentiment')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if sentiment_filter:
        cursor.execute('SELECT * FROM reviews WHERE sentiment = ?', (sentiment_filter,))
    else:
        cursor.execute('SELECT * FROM reviews')
    
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(reviews), 200


if __name__ == '__main__':
    init_db()
    app.run()
