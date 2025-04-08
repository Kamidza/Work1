CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    registered_at TIMESTAMP NOT NULL
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    topic_id INT REFERENCES topics(id),
    user_id INT REFERENCES users(id),  -- может быть NULL для анонимов
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TYPE log_action AS ENUM (
    'visit',
    'register',
    'login',
    'logout',
    'create_topic',
    'view_topic',
    'delete_topic',
    'post_message'
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action log_action NOT NULL,
    action_target_id INT,
    status VARCHAR(10),
    description TEXT,
    created_at TIMESTAMP NOT NULL
);