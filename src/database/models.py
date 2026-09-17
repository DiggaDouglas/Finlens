from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class CreditProvider(BaseModel):
    lender_name: str
    cbk_license_status: bool
    platform_url: Optional[str] = None

class LegalDocument(BaseModel):
    provider_id: str
    doc_type: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    raw_text: str
    uploaded_by: str

class ViolationClause(BaseModel):
    clause_text: str
    violation_category: str
    regulatory_section: str
    xai_attribution: Dict[str, float]

class ComplianceReport(BaseModel):
    document_id: str
    overall_risk_score: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    violations: List[ViolationClause]