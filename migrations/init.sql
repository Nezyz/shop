CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    coins INTEGER DEFAULT 1000
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount INTEGER NOT NULL,
    type VARCHAR(10) NOT NULL,
    user_id INTEGER REFERENCES users(id)
);