from pydantic import BaseModel, field_validator

from ..enums.extractor_document_types import DocumentROIs

class ExtractorRequest(BaseModel):
    """Classe per gestire la request del POST"""
    tipologia_documento: str

    @field_validator("tipologia_documento", mode="before")
    def validate_tipologia_documento(cls, v: object):
        if v not in [d.value for d in DocumentROIs]:
            raise ValueError("Valore non valido")
        return v
