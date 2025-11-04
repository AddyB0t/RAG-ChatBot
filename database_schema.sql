CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(128) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    raw_text TEXT,
    structured_data JSONB,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL,
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    completeness_score INTEGER CHECK (completeness_score >= 0 AND completeness_score <= 100),
    industry_classifications JSONB,
    career_level VARCHAR(50),
    salary_estimate JSONB,
    suggestions JSONB,
    confidence_scores JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resume_job_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    job_description TEXT NOT NULL,
    job_requirements JSONB,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    recommendation VARCHAR(50),
    category_scores JSONB,
    strength_areas JSONB,
    gap_analysis JSONB,
    salary_alignment JSONB,
    competitive_advantages JSONB,
    explanation JSONB,
    processing_metadata JSONB,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resume_parser_error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    extractor_name VARCHAR(100),
    input_data JSONB,
    context JSONB,
    severity VARCHAR(20) DEFAULT 'error',
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_resumes_file_hash ON resumes(file_hash);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status);
CREATE INDEX IF NOT EXISTS idx_resumes_uploaded_at ON resumes(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_resume_id ON ai_analysis(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_job_matches_resume_id ON resume_job_matches(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_job_matches_overall_score ON resume_job_matches(overall_score);
CREATE INDEX IF NOT EXISTS idx_resumes_structured_data_gin ON resumes USING GIN (structured_data);
CREATE INDEX IF NOT EXISTS idx_error_logs_resume_id ON resume_parser_error_logs(resume_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON resume_parser_error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON resume_parser_error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_is_resolved ON resume_parser_error_logs(is_resolved);
CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON resume_parser_error_logs(created_at);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
