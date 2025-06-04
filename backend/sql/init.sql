CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    mfa TEXT,
    gendate BIGINT,
    expired BOOLEAN
);
