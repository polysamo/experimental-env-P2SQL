CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(180) UNIQUE NOT NULL,
    role_name VARCHAR(50) NOT NULL,
    city VARCHAR(80),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_posts (
    job_post_id SERIAL PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    department VARCHAR(120) NOT NULL,
    location VARCHAR(80),
    salary_range VARCHAR(80),
    status VARCHAR(30) NOT NULL,
    posted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS applications (
    application_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    job_post_id INT NOT NULL REFERENCES job_posts(job_post_id),
    application_status VARCHAR(40) NOT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_notes (
    note_id SERIAL PRIMARY KEY,
    related_user_id INT REFERENCES users(user_id),
    note_text TEXT NOT NULL,
    note_tag VARCHAR(50),
    sensitivity_level VARCHAR(20) NOT NULL DEFAULT 'restricted',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id SERIAL PRIMARY KEY,
    prompt_id TEXT,
    scenario_name TEXT,
    prompt_text TEXT,
    generated_sql TEXT,
    final_decision TEXT,
    defense_layer_triggered TEXT,
    response_preview TEXT,
    rows_returned INTEGER,
    latency_ms INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);