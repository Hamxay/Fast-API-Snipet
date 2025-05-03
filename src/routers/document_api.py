import os
from typing import Annotated, List
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy.orm import Session
from src.types.document_response_type import (
    DownloadDocumentResponse,
    QueryResponse,
    UploadResponse,
    SourceDocument,
)
from src.utils.config import OPENAI_API_KEY
from src.providers.openai_client import OpenAIClient
from src.types.pipecode_data_types import QueryResult
from src.utils.doc_utils import (
    get_chuncks_similar_to_text,
    process_file_document,
    save_file,
)
from src.database import get_db
from src.models.file_document import FileDocument


router = APIRouter(tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="Image file")],
    db: Session = Depends(get_db),
) -> UploadResponse:
    assert file.filename

    content_type = file.content_type

    if not (content_type.startswith("image/") or content_type == "application/pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image or PDF files are allowed.",
        )

    file_data = await file.read()
    file.file.seek(0)  # Reset the file pointer to the beginning

    file_path = await save_file(file)

    try:
        # Store file information in database
        db_file = FileDocument(file_name=file.filename, storage_path=file_path)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # process file document to extract text and upsert to Pinecone
        await process_file_document(file_data, file.filename)
    except Exception as e:
        logger.error(f"Error processing file document: {e}")
        raise HTTPException(
            status_code=500, detail="Error processing file document."
        ) from e

    return UploadResponse(
        message=f"Text data from file '{file.filename}' successfully upserted to Pinecone."
    )


@router.get("/query")
async def query_document(
    query_text: str,
    request: Request,
) -> QueryResponse:
    matched_pinecone_chucks: QueryResult | None = await get_chuncks_similar_to_text(
        query_text
    )

    if not matched_pinecone_chucks:
        raise HTTPException(status_code=404, detail="No relevant data found.")

    # Format context and query
    context = "\n".join(
        [f"Text {i+1}: {chunk.text}" for i, chunk in enumerate(matched_pinecone_chucks)]
    )

    source_documents = []
    seen_filenames = set()

    for chunk in matched_pinecone_chucks:
        if chunk.id not in seen_filenames:
            seen_filenames.add(chunk.id)
            download_url = str(request.url_for("download_document", filename=chunk.id))
            source_documents.append(
                SourceDocument(filename=chunk.id, download_url=download_url)
            )

    # Call OpenAI to get an answer based on the context
    try:
        client = OpenAIClient(api_key=OPENAI_API_KEY)
        answer = await client.get_answer_to_question(query_text, context)
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(
            status_code=500, detail="Error generating the answer from the model."
        ) from e

    return QueryResponse(answer=answer, sources=source_documents)


@router.get("/download/{filename}")
async def download_document(filename: str, request: Request):
    try:
        file_path = os.path.join("uploads", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        download_url = str(request.url_for("download_document", filename=filename))

        return DownloadDocumentResponse(download_url=download_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/search-documents/{search_term}")
async def search_documents(
    search_term: str, db: Session = Depends(get_db)
) -> List[dict]:
    try:
        # Search for documents where filename contains the search term
        documents = (
            db.query(FileDocument)
            .filter(FileDocument.file_name.ilike(f"%{search_term}%"))
            .all()
        )

        if not documents:
            raise HTTPException(
                status_code=404, detail="No documents found matching the search term."
            )

        return [
            {"id": doc.id, "file_name": doc.file_name, "storage_path": doc.storage_path}
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=500, detail="Error searching for documents."
        ) from e
