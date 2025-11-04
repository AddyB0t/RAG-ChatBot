from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from app.core.database import Base
import uuid

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_hash = Column(String(128), unique=True, nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='pending', index=True)
    raw_text = Column(Text)
    structured_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    error_logs = relationship("ResumeParserErrorLog", back_populates="resume", cascade="all, delete-orphan")
    job_matches = relationship("ResumeJobMatch", back_populates="resume", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="resume", cascade="all, delete-orphan")

class ResumeJobMatch(Base):
    __tablename__ = "resume_job_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    job_description = Column(Text, nullable=False)
    job_requirements = Column(JSONB)
    overall_score = Column(Integer, index=True)
    confidence_score = Column(Numeric(3, 2))
    recommendation = Column(String(50))
    category_scores = Column(JSONB)
    strength_areas = Column(JSONB)
    gap_analysis = Column(JSONB)
    salary_alignment = Column(JSONB)
    competitive_advantages = Column(JSONB)
    explanation = Column(JSONB)
    processing_metadata = Column(JSONB)
    matched_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="job_matches")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    quality_score = Column(Integer)
    completeness_score = Column(Integer)
    industry_classifications = Column(JSONB)
    career_level = Column(String(50))
    salary_estimate = Column(JSONB)
    suggestions = Column(JSONB)
    confidence_scores = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="ai_analysis")

class ResumeParserErrorLog(Base):
    __tablename__ = "resume_parser_error_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True, index=True)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    extractor_name = Column(String(100))
    input_data = Column(JSONB)
    context = Column(JSONB)
    severity = Column(String(20), default='error', index=True)
    is_resolved = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    resume = relationship("Resume", back_populates="error_logs")

