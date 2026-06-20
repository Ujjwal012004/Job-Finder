-- ============================================
-- Job Finder — Database Schema (PostgreSQL)
-- ============================================
-- This file contains the raw DDL statements
-- matching the SQLAlchemy ORM models.
-- Use this for manual review of normalization,
-- constraints, and referential integrity.
-- ============================================

-- 1. Users
CREATE TABLE users (
    id              SERIAL          PRIMARY KEY,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(150)    NOT NULL,
    phone           VARCHAR(20),
    resume_url      TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- 2. Companies
CREATE TABLE companies (
    id              SERIAL          PRIMARY KEY,
    name            VARCHAR(255)    NOT NULL UNIQUE,
    website         VARCHAR(500),
    logo_url        TEXT,
    industry        VARCHAR(100),
    description     TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies(name);

-- 3. Jobs
CREATE TABLE jobs (
    id                  SERIAL          PRIMARY KEY,
    company_id          INTEGER         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title               VARCHAR(300)    NOT NULL,
    description         TEXT,
    location            VARCHAR(255),
    employment_type     VARCHAR(50)     NOT NULL DEFAULT 'full-time'
                        CHECK (employment_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance')),
    experience_level    VARCHAR(50)
                        CHECK (experience_level IN ('entry', 'mid', 'senior', 'lead', 'executive')),
    salary_min          NUMERIC(12, 2),
    salary_max          NUMERIC(12, 2),
    salary_currency     VARCHAR(3)      DEFAULT 'USD',
    source              VARCHAR(100),
    source_url          TEXT,
    is_remote           BOOLEAN         NOT NULL DEFAULT FALSE,
    status              VARCHAR(20)     NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'closed', 'expired')),
    posted_at           TIMESTAMP,
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_salary_range CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
);

CREATE INDEX idx_jobs_company    ON jobs(company_id);
CREATE INDEX idx_jobs_title      ON jobs(title);
CREATE INDEX idx_jobs_location   ON jobs(location);
CREATE INDEX idx_jobs_status     ON jobs(status);
CREATE INDEX idx_jobs_remote     ON jobs(is_remote);

-- 4. Applications
CREATE TABLE applications (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id              INTEGER         NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status              VARCHAR(30)     NOT NULL DEFAULT 'applied'
                        CHECK (status IN ('applied', 'screening', 'interviewing', 'offered', 'accepted', 'rejected', 'withdrawn')),
    applied_on          DATE            NOT NULL DEFAULT CURRENT_DATE,
    cover_letter        TEXT,
    resume_snapshot_url TEXT,
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_job_application UNIQUE (user_id, job_id)
);

CREATE INDEX idx_applications_user   ON applications(user_id);
CREATE INDEX idx_applications_job    ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);

-- 5. Saved Jobs (Bookmarks)
CREATE TABLE saved_jobs (
    id          SERIAL      PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id      INTEGER     NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    saved_at    TIMESTAMP   NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_saved_job UNIQUE (user_id, job_id)
);

CREATE INDEX idx_saved_jobs_user ON saved_jobs(user_id);

-- 6. Application Notes
CREATE TABLE application_notes (
    id              SERIAL      PRIMARY KEY,
    application_id  INTEGER     NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    content         TEXT        NOT NULL,
    note_type       VARCHAR(30) NOT NULL DEFAULT 'general'
                    CHECK (note_type IN ('general', 'interview_prep', 'follow_up', 'feedback')),
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_application ON application_notes(application_id);
