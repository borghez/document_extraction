import os

from tempfile import mkstemp
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, UploadFile, APIRouter, status, Form

from . import ExtractorResponse
from . import ImageUploadException 
from . import AvailableExtensions, DocumentROIs, IdExtractor


extractor_router = APIRouter(prefix="/ai-id-extractor", tags=['ai-id-extractor'])
app = FastAPI()

@app.exception_handler(RequestValidationError)
async def request_exception_handler(tipologia_documento: str, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"esito": "ko", "message": str(exc)})
    )

@app.exception_handler(ImageUploadException)
async def image_exception_handler(image: UploadFile, exc: ImageUploadException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"esito": "ko", "message": str(exc)})
    )




@extractor_router.get("/get_tipologie_documenti", status_code=200)
async def tipologie_documenti():
    document_types = [d.name for d in DocumentROIs]
    return JSONResponse(content={"esito": "ok", "messages": "", "tipologie_documenti": document_types}, status_code=200)

@extractor_router.post("/extract", status_code=201)
async def extract(file: UploadFile, tipologia_documento: str = Form()):
    if tipologia_documento not in [d.name for d in DocumentROIs]:
        raise RequestValidationError("Tipologia documento non ammissibile")
    
    if file.filename.split(".")[-1] not in [e.value for e in AvailableExtensions]:
        raise ImageUploadException("Formato immagine non valido")

    try:
        stream = file.file.read()
        temp_file, path = mkstemp()
        with os.fdopen(temp_file, "wb") as f:
            f.write(stream)

        extractor = IdExtractor(path, tipologia_documento)
        result = extractor.extraction()

        if result["extracted_texts"] is None or not isinstance(result["extracted_texts"], list):
            raise Exception("Qualcosa è andato storto")

        resp = [ExtractorResponse(**r).model_dump() for r in result["extracted_texts"]]
        os.remove(path)
        
        return JSONResponse(content={"esito": "ok", "message": "", "entities": resp, "method": result["method"]}, status_code=200)
    except Exception as ex:
        return JSONResponse(content={"esito": "ko", "messages": str(ex)}, status_code=500)


app.include_router(extractor_router)