from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.utils.db import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business_profiles = relationship("BusinessProfile", back_populates="user", cascade="all, delete-orphan")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=False)
    company_size = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)

    user = relationship("User", back_populates="business_profiles")
    metrics = relationship("BusinessMetric", back_populates="business", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="business", cascade="all, delete-orphan")
    session_memory = relationship("SessionMemory", back_populates="business", uselist=False, cascade="all, delete-orphan")

class BusinessMetric(Base):
    __tablename__ = "business_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    electricity_usage = Column(Numeric(12, 2), default=0.0)
    diesel_usage = Column(Numeric(12, 2), default=0.0)
    petrol_usage = Column(Numeric(12, 2), default=0.0)
    water_usage = Column(Numeric(12, 2), default=0.0)
    waste_generated = Column(Numeric(12, 2), default=0.0)
    annual_revenue = Column(Numeric(15, 2), default=0.0)
    sustainability_budget = Column(Numeric(15, 2), default=0.0)

    business = relationship("BusinessProfile", back_populates="metrics")

class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(Integer, primary_key=True, index=True)
    activity = Column(String(100), unique=True, nullable=False)
    unit = Column(String(50), nullable=False)
    emission_factor = Column(Numeric(10, 6), nullable=False)

class SustainabilityMeasure(Base):
    __tablename__ = "sustainability_measures"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    expected_reduction = Column(Numeric(5, 2), nullable=False)

    costs = relationship("TechnologyCost", back_populates="measure", cascade="all, delete-orphan")
    sdg_mappings = relationship("SdgMapping", back_populates="measure", cascade="all, delete-orphan")

class TechnologyCost(Base):
    __tablename__ = "technology_costs"

    id = Column(Integer, primary_key=True, index=True)
    measure_id = Column(Integer, ForeignKey("sustainability_measures.id", ondelete="CASCADE"), nullable=False)
    implementation_cost = Column(Numeric(15, 2), nullable=False)
    annual_savings = Column(Numeric(15, 2), nullable=False)
    maintenance_cost = Column(Numeric(15, 2), nullable=False)
    roi_years = Column(Numeric(5, 2), nullable=False)

    measure = relationship("SustainabilityMeasure", back_populates="costs")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    workflow_status = Column(String(50), default="Draft")
    current_agent = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0)
    shared_state = Column(JSONB, nullable=True)

    business = relationship("BusinessProfile", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")
    tool_logs = relationship("ToolLog", back_populates="analysis", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    report_json = Column(JSONB, nullable=False)
    pdf_url = Column(String(500), nullable=True)
    approved = Column(Boolean, default=False)
    overall_score = Column(Numeric(5, 2), nullable=True)

    analysis = relationship("Analysis", back_populates="reports")
    feedbacks = relationship("Feedback", back_populates="report", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="report", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    feedback = Column(String(2000), nullable=False)

    report = relationship("Report", back_populates="feedbacks")

class SessionMemory(Base):
    __tablename__ = "session_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("business_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    previous_reports = Column(JSONB, nullable=True)
    previous_recommendations = Column(JSONB, nullable=True)
    last_analysis = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    business = relationship("BusinessProfile", back_populates="session_memory")

class ToolLog(Base):
    __tablename__ = "tool_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    agent = Column(String(50), nullable=False)
    tool = Column(String(100), nullable=False)
    duration = Column(Numeric(10, 3), nullable=False) # Execution duration in seconds
    status = Column(String(50), nullable=False)

    analysis = relationship("Analysis", back_populates="tool_logs")

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    recipient = Column(String(255), nullable=False)
    delivery_status = Column(String(50), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="email_logs")

# Extra tables from seed guide
class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

class SustainabilityGoal(Base):
    __tablename__ = "sustainability_goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

class SdgMapping(Base):
    __tablename__ = "sdg_mapping"

    id = Column(Integer, primary_key=True, index=True)
    measure_id = Column(Integer, ForeignKey("sustainability_measures.id", ondelete="CASCADE"), nullable=False)
    sdg_number = Column(Integer, nullable=False)
    sdg_name = Column(String(255), nullable=False)

    measure = relationship("SustainabilityMeasure", back_populates="sdg_mappings")

class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String(100), unique=True, nullable=False)
    benchmark_emissions = Column(Numeric(15, 2), nullable=False)
