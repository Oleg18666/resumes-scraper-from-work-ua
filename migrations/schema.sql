-- Database schema for Work.ua resume scraper
-- PostgreSQL 12+

-- Main resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL,
    resume_date DATE NOT NULL,
    person_name TEXT NOT NULL,
    position TEXT NOT NULL,
    source_url TEXT NOT NULL,
    
    -- Optional fields
    desired_salary INTEGER,
    employment_type SMALLINT,  -- 1=full_time, 2=part_time, 3=remote, 4=project, 5=internship
    birthday DATE,
    city TEXT,
    gender SMALLINT,  -- 1=male, 2=female, 3=not_specified
    education_level TEXT,
    work_experience_years NUMERIC(5,2),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint: same resume_id can have multiple entries for different dates
    CONSTRAINT unique_resume_date UNIQUE (resume_id, resume_date)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_resumes_resume_id ON resumes(resume_id);
CREATE INDEX IF NOT EXISTS idx_resumes_city ON resumes(city);
CREATE INDEX IF NOT EXISTS idx_resumes_position ON resumes(position);
CREATE INDEX IF NOT EXISTS idx_resumes_created_at ON resumes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_resumes_employment_type ON resumes(employment_type);


-- Extended resume details (raw text fields)
CREATE TABLE IF NOT EXISTS resume_details (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    work_experience_raw TEXT,
    education_raw TEXT,
    additional_education_raw TEXT,
    skills_raw TEXT,
    languages_raw TEXT,
    recommendations_raw TEXT,
    additional_info_raw TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_resume_details UNIQUE (resume_id)
);

CREATE INDEX IF NOT EXISTS idx_resume_details_resume_id ON resume_details(resume_id);


-- Resume photos
CREATE TABLE IF NOT EXISTS resume_photos (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    photo BYTEA NOT NULL,
    content_type VARCHAR(50) DEFAULT 'image/jpeg',
    hash VARCHAR(64),  -- MD5 or SHA256 for deduplication
    file_size INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_resume_photo UNIQUE (resume_id)
);

CREATE INDEX IF NOT EXISTS idx_resume_photos_hash ON resume_photos(hash);
CREATE INDEX IF NOT EXISTS idx_resume_photos_resume_id ON resume_photos(resume_id);


-- Search pages tracking (for pagination and resume discovery)
CREATE TABLE IF NOT EXISTS search_pages (
    id SERIAL PRIMARY KEY,
    category INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    url TEXT NOT NULL,
    days_filter INTEGER,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, done, error
    last_error TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_search_page UNIQUE (category, city_id, page_number, days_filter)
);

CREATE INDEX IF NOT EXISTS idx_search_pages_status ON search_pages(status);
CREATE INDEX IF NOT EXISTS idx_search_pages_category_city ON search_pages(category, city_id);


-- Resume tasks queue (alternative to external queue)
CREATE TABLE IF NOT EXISTS resume_tasks (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, done, error
    last_error TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_resume_task UNIQUE (resume_id)
);

CREATE INDEX IF NOT EXISTS idx_resume_tasks_status ON resume_tasks(status);
CREATE INDEX IF NOT EXISTS idx_resume_tasks_created_at ON resume_tasks(created_at);


-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_pages_updated_at BEFORE UPDATE ON search_pages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resume_tasks_updated_at BEFORE UPDATE ON resume_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Statistics view
CREATE OR REPLACE VIEW resume_stats AS
SELECT
    COUNT(*) as total_resumes,
    COUNT(DISTINCT resume_id) as unique_resume_ids,
    COUNT(DISTINCT city) as cities_count,
    COUNT(DISTINCT position) as positions_count,
    MIN(created_at) as first_scraped,
    MAX(created_at) as last_scraped,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as scraped_last_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as scraped_last_7d
FROM resumes;
