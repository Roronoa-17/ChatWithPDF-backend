import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from app.schemas.document import DocumentUploadResponse
from app.services.ingestion import ingest_pdf

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse) 
async def upload_pdf(file: UploadFile = File(...), namespace: str = Form(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported.",
        )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        total_chunks = ingest_pdf(tmp_path, namespace)
        return DocumentUploadResponse(
            filename=file.filename,
            total_chunks=total_chunks,
            message="Document successfully parsed, vectorized, and indexed in Pinecone.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(exc)}",
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)