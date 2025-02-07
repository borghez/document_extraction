from pydantic import BaseModel, field_validator
from pydantic.types import StrictInt, StrictFloat, StrictStr

class ExtractorResponse(BaseModel):
    """Classe per gestire la response del POST"""
    category: str
    value: str|int|float|None
    confidence: float|int
