from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text)
    benefits: Mapped[list] = mapped_column(JSON, default=list)
    eligibility: Mapped[list] = mapped_column(JSON, default=list)
    documents: Mapped[list] = mapped_column(JSON, default=list)
    application_procedure: Mapped[list] = mapped_column(JSON, default=list)
    state_scope: Mapped[str] = mapped_column(String(120), default="India")
    official_url: Mapped[str] = mapped_column(String(500))
    verification_notes: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Demo Citizen")

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(80), nullable=True)
    income_range: Mapped[str | None] = mapped_column(String(80), nullable=True)
    farmer_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    land_ownership: Mapped[str | None] = mapped_column(String(80), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(40), default="auto")

class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200), default="New conversation")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)

class SavedScheme(Base):
    __tablename__ = "saved_schemes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"))

class EligibilitySession(Base):
    __tablename__ = "eligibility_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="in_progress")

class EligibilityAnswer(Base):
    __tablename__ = "eligibility_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("eligibility_sessions.id"))
    field: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)

class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scheme_id: Mapped[int | None] = mapped_column(ForeignKey("schemes.id"), nullable=True)
    scheme_name: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(40), default="Not Started")
    current_step: Mapped[str] = mapped_column(String(180), default="Review scheme requirements")
    documents: Mapped[list] = mapped_column(JSON, default=list)
    next_action: Mapped[str] = mapped_column(Text, default="Review the required documents")
    timeline: Mapped[list] = mapped_column(JSON, default=list)

class Grievance(Base):
    __tablename__ = "grievances"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    complaint: Mapped[str] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)
    suggested_department: Mapped[str] = mapped_column(String(160))
    next_step: Mapped[str] = mapped_column(Text)
    required_evidence: Mapped[list] = mapped_column(JSON, default=list)

class CooperativeService(Base):
    __tablename__ = "cooperative_services"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text)
    steps: Mapped[list] = mapped_column(JSON, default=list)
    documents: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="Verify current requirements with the relevant cooperative authority.")
