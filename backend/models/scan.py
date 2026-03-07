from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanResponse(BaseModel):
    id: str
    user_id: str
    file_url: str
    file_name: str
    doc_type: Optional[str] = None
    model_used: Optional[str] = None
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    scanned_at: datetime
