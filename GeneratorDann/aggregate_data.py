
import csv
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def aggregate(start_date, end_date):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()

    query = """
    WITH daily_users AS (
        SELECT DATE(registered_at) AS day, COUNT(*) AS new_accounts
        FROM users
        WHERE registered_at BETWEEN %s AND %s
        GROUP BY day
    ),
    daily_messages AS (
        SELECT DATE(created_at) AS day,
               COUNT(*) AS total_messages,
               COUNT(*) FILTER (WHERE user_id IS NULL) * 100.0 / COUNT(*) AS anon_percentage
        FROM messages
        WHERE created_at BETWEEN %s AND %s
        GROUP BY day
    ),
    daily_topics AS (
        SELECT DATE(created_at) AS day, COUNT(*) AS new_topics
        FROM topics
        WHERE created_at BETWEEN %s AND %s
        GROUP BY day
    )
    SELECT
        d.day,
        COALESCE(u.new_accounts, 0),
        COALESCE(m.total_messages, 0),
        ROUND(COALESCE(m.anon_percentage, 0), 2),
        COALESCE(t.new_topics, 0)
    FROM generate_series(%s::date, %s::date, interval '1 day') d(day)
    LEFT JOIN daily_users u ON d.day = u.day
    LEFT JOIN daily_messages m ON d.day = m.day
    LEFT JOIN daily_topics t ON d.day = t.day
    ORDER BY d.day;
    """

    cur.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date))
    rows = cur.fetchall()

    result = []
    prev_topics = None
    for row in rows:
        date, accounts, messages, anon_pct, topics = row
        if prev_topics is not None:
            change_pct = ((topics - prev_topics) / prev_topics) * 100 if prev_topics > 0 else 0
        else:
            change_pct = 0
        prev_topics = topics
        result.append([date, accounts, anon_pct, messages, round(change_pct, 2)])

    with open('aggregation.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['day', 'new_accounts', 'anon_msg_%', 'total_msgs', 'topics_change_%'])
        writer.writerows(result)

    cur.close()
    conn.close()
    print("Aggregation saved to aggregation.csv")

if name == "main":
    aggregate("2024-03-01", "2024-03-31")