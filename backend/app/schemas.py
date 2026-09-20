from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    conversation_id: int | None = None
    profile: dict = {}

class ChatResponse(BaseModel):
    conversation_id: int
    language: str
    intent: str
    entities: dict
    response: str
    schemes: list[dict]

class SchemeOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    benefits: list
    eligibility: list
    documents: list
    application_procedure: list
    state_scope: str
    official_url: str
    verification_notes: str
    class Config:
        from_attributes = True

class ProfileIn(BaseModel):
    name: str | None = None
    age: int | None = None
    state: str | None = None
    district: str | None = None
    occupation: str | None = None
    income_range: str | None = None
    farmer_status: str | None = None
    land_ownership: str | None = None
    preferred_language: str = "auto"


class EligibilityRequest(BaseModel):
    session_id: int | None = None
    answers: dict = {}

class EligibilityResponse(BaseModel):
    session_id: int
    current_step: int
    complete: bool
    missing_fields: list[str]
    results: list[dict]
    disclaimer: str
