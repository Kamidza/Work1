from dotenv import load_dotenv
load_dotenv("w.env")
import random
from datetime import datetime, timedelta
import psycopg2
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()
fake = Faker()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

users = []
usernames = set()

# Создание пользователей
for _ in range(30):
    username = fake.user_name()
    while username in usernames:
        username = fake.user_name()
    usernames.add(username)
    registered_at = fake.date_time_between(start_date='-1y', end_date='-1d')
    cur.execute("INSERT INTO users (username, registered_at) VALUES (%s, %s) RETURNING id", (username, registered_at))
    users.append(cur.fetchone()[0])

conn.commit()

actions = [
    'visit', 'register', 'login', 'logout',
    'create_topic', 'view_topic', 'delete_topic', 'post_message'
]

start_date = datetime.today() - timedelta(days=30)

for day in range(30):
    current_day = start_date + timedelta(days=day)
    topics_created = 0
    for action in actions:
        count = 5 + random.randint(0, 10)
        for _ in range(count):
            user_id = random.choice(users) if action != 'post_message' or random.random() > 0.5 else None
            status = 'success'
            description = f"{action} performed"
            action_target_id = None
            time = current_day + timedelta(seconds=random.randint(0, 86400))

            if action == 'create_topic':
                if user_id is None or random.random() < 0.2:
                    status = 'error'
                    description = 'User not logged in'
                else:
                    title = fake.sentence()
                    cur.execute("INSERT INTO topics (user_id, title, created_at) VALUES (%s, %s, %s) RETURNING id", (user_id, title, time))
                    action_target_id = cur.fetchone()[0]
                    topics_created += 1

            elif action == 'post_message':
                topic_id = random.randint(1, topics_created or 1)
                content = fake.text()
                cur.execute(
                    "INSERT INTO messages (topic_id, user_id, content, created_at) VALUES (%s, %s, %s, %s)",
                    (topic_id, user_id, content, time)
                )
                action_target_id = topic_id

            elif action in ['view_topic', 'delete_topic']:
                action_target_id = random.randint(1, topics_created or 1)

            cur.execute(
                "INSERT INTO logs (user_id, action, action_target_id, status, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, action, action_target_id, status, description, time)
            )

conn.commit()
cur.close()
conn.close()
print("Data generation complete.")