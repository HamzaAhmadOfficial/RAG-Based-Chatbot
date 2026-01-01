# Project Report: Professional RAG-Based Document Assistant
**Course:** Computational Intelligence - Semester Project
**Date:** January 1, 2026

---

## 1. Introduction
The **Professional RAG Assistant** is a Retrieval-Augmented Generation (RAG) system designed to provide intelligent, context-aware answers from PDF documents. By combining the power of Large Language Models (LLMs) with efficient vector retrieval, the system allows users to interact with their documents in a natural language format, ensuring that the AI's responses are grounded in specific, verifiable source material.

## 2. Technical Architecture
The system follows a standard RAG pipeline, divided into two main phases: **Ingestion** and **Retrieval/Generation**.

### 2.1 Ingestion Pipeline
1. **Document Loading**: PDF files are processed using `PyPDF2` to extract raw text.
2. **Chunking**: Extracted text is split into smaller, manageable segments (approx. 1000 characters with 200-character overlap) to preserve context.
3. **Embedding Generation**: Chunks are converted into 384-dimensional dense vectors using the `sentence-transformers/all-MiniLM-L6-v2` model.
4. **Vector Storage**: Use of **FAISS (Facebook AI Similarity Search)** for high-efficiency local storage and similarity indexing of embeddings.

### 2.2 Retrieval & Generation Flow
1. **Query Processing**: The user's question is converted into an embedding using the same transformer model.
2. **Semantic Search**: FAISS performs a similarity search to retrieve the top 3 most relevant document chunks.
3. **Augmentation**: The retrieved chunks are injected into a specialized prompt alongside the user's query.
4. **LLM Generation**: The augmented prompt is sent to the **Meta Llama 3 (8B)** model via the Hugging Face Inference API to generate a grounded response.

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Programming Language** | Python 3.10+ |
| **Backend Framework** | FastAPI |
| **LLM Interface** | Hugging Face Hub (Llama-3-8B-Instruct) |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **Vector Database** | FAISS (CPU-optimized) |
| **Metadata Database** | SQLite |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript |
| **PDF Processing** | PyPDF2 |

## 4. Key Features
- **Semantic Search**: Understands the meaning of queries rather than just keyword matching.
- **Source Attribution**: Provides specific citations from the uploaded document for every answer.
- **Professional UI**: A clean, corporate-themed interface optimized for academic and professional use.
- **Session Persistence**: Maintains conversation history via a localized SQLite database.
- **Windows Optimized**: Full compatibility with Windows systems using FAISS without requiring heavy C++ build tools.

## 5. System Implementation

### 5.1 Backend Logic
- `main.py`: Orchestrates the REST API endpoints for uploading documents and questioning the assistant.
- `chat_bot.py`: Handles the interaction with the Llama 3 model and prompt engineering.
- `vector_db.py`: Manages the FAISS index and embedding generation logic.
- `pdf_handler.py`: Dedicated module for robust PDF parsing and intelligent chunking.

### 5.2 Frontend Interface
The UI is built with a focus on usability and professional aesthetics, featuring:
- **Responsive Design**: Compatible across various screen sizes.
- **Real-time Feedback**: Includes "Analyzing..." indicators and status updates for file processing.
- **Classic Layout**: A clear separation of document management and chat interaction.

## 6. Setup and Installation
1. **Environment Setup**: Define the Hugging Face API key in a `.env` file.
2. **Dependency Installation**: Install required libraries via `pip install -r requirements.txt`.
3. **Execution**: Run the system using `python run_app.py`, which initializes the server and opens the web interface.

## 7. Conclusion
This project demonstrates the effective integration of modern computational intelligence techniques to solve real-world information retrieval problems. By leveraging RAG architecture, the system mitigates the risk of LLM hallucinations and provides a reliable tool for deep document analysis.
