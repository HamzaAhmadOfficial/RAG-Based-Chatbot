"""
Main FastAPI Application
Provides REST API endpoints for the RAG chatbot
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import shutil
from typing import Optional
import uuid

from pdf_handler import PDFHandler
from vector_db import VectorDatabase
from database import Database
from chat_bot import ChatBot


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for PDF documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_handler = PDFHandler(chunk_size=1000, chunk_overlap=200)
vector_db = VectorDatabase(persist_directory="./vector_db")
database = Database(db_path="chat_history.db")
chatbot = ChatBot(vector_db=vector_db)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Session ID (simple implementation)
SESSION_ID = str(uuid.uuid4())


# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class QuestionResponse(BaseModel):
    answer: str
    sources: list
    session_id: str


# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("frontend/index.html")


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file
    
    Args:
        file: PDF file to upload
        
    Returns:
        Success message with processing details
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        print(f"Processing PDF: {file.filename}")
        chunks = pdf_handler.process_pdf(file_path)
        
        # Add to vector database
        print(f"Adding {len(chunks)} chunks to vector database...")
        vector_db.create_collection("documents")
        vector_db.add_documents(chunks, "documents")
        
        # Save to database
        database.add_document(
            filename=file.filename,
            file_path=file_path,
            num_chunks=len(chunks)
        )
        
        return JSONResponse(content={
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "num_chunks": len(chunks),
            "status": "success"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded documents
    
    Args:
        request: Question request with question text
        
    Returns:
        Answer with sources
    """
    try:
        # Get session ID
        session_id = request.session_id or SESSION_ID
        
        # Get answer from chatbot
        result = chatbot.answer_question(request.question, n_context_docs=3)
        
        # Save to database
        database.add_chat_message(
            session_id=session_id,
            user_message=request.question,
            bot_response=result['answer'],
            sources=result.get('sources', [])
        )
        
        return QuestionResponse(
            answer=result['answer'],
            sources=result.get('sources', []),
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@app.get("/history")
async def get_history(session_id: Optional[str] = None, limit: int = 50):
    """
    Get chat history
    
    Args:
        session_id: Optional session ID to filter
        limit: Maximum number of messages
        
    Returns:
        Chat history
    """
    try:
        history = database.get_chat_history(session_id=session_id, limit=limit)
        return JSONResponse(content={"history": history})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@app.get("/documents")
async def get_documents():
    """
    Get list of uploaded documents
    
    Returns:
        List of documents
    """
    try:
        documents = database.get_documents()
        return JSONResponse(content={"documents": documents})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")


@app.delete("/clear")
async def clear_database():
    """
    Clear vector database and chat history
    
    Returns:
        Success message
    """
    try:
        # Reset vector database
        vector_db.reset_database()
        
        # Clear chat history
        database.clear_history()
        
        return JSONResponse(content={
            "message": "Database cleared successfully",
            "status": "success"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "vector_db_count": vector_db.get_collection_count()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
