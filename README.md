# RAG Chatbot – Document Question Answering System

This project implements a Retrieval-Augmented Generation (RAG) based chatbot that allows users to upload PDF documents and ask questions about their content. The system retrieves relevant information from the uploaded documents and generates accurate, context-aware answers using Hugging Face language models.

This project is developed as a Computational Intelligence semester project.

---

## Features

- PDF document upload and processing
- Automatic text extraction and chunking
- Semantic search using FAISS vector database
- Question answering using Hugging Face language models
- Web-based chat interface
- Source-based answers using retrieved document context
- Chat history stored in SQLite
- Simple and clean user interface
- Fully compatible with Windows

---

## System Architecture

Frontend (HTML, CSS, JavaScript)
        |
        v
FastAPI Backend
        |
        v
Vector Database (FAISS)
        |
        v
Hugging Face API (Embeddings and LLM)

---

## Requirements

- Python 3.11 or higher
- Hugging Face API key
- Minimum 4 GB RAM recommended

---

## Setup Instructions

1. Navigate to the project directory

cd "d:/7TH SEMESTER/Computational Intelligence/Sem Project"

2. Install dependencies

pip install -r requirements.txt

3. Configure environment variables

Create or update the .env file and add:

HUGGINGFACE_API_KEY=your_api_key_here

4. First-time setup

python first_run.py

This step creates required directories, verifies dependencies, and validates configuration.

5. Run the application

python run_app.py

The application will start at:
http://localhost:8000

---

## Usage

### Uploading Documents

1. Open the web interface in a browser
2. Upload a PDF document
3. Wait for processing to complete
4. The chat input becomes available after processing

### Asking Questions

1. Enter a question related to the uploaded document
2. Submit the question
3. Relevant document sections are retrieved
4. The answer is generated using retrieved context

---

## Project Structure

SEMESTER PROJECT/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── vector_db/
├── uploads/
├── chat_bot.py
├── database.py
├── main.py
├── pdf_handler.py
├── vector_db.py
├── run_app.py
├── first_run.py
├── requirements.txt
├── Dockerfile
├── .env
└── README.md

---

## API Endpoints

/              GET     Load frontend interface
/upload-pdf    POST    Upload and process PDF
/ask           POST    Ask a question
/history       GET     Retrieve chat history
/documents     GET     List uploaded documents
/clear         DELETE  Clear stored data
/health        GET     Health check

---

## Docker Support

Build image:
docker build -t rag-chatbot .

Run container:
docker run -p 8000:8000 -e HUGGINGFACE_API_KEY=your_key rag-chatbot

---

## Configuration

Change language model in chat_bot.py:

self.llm_model = "mistralai/Mistral-7B-Instruct-v0.2"

Modify chunk size in main.py:

PDFHandler(chunk_size=1000, chunk_overlap=200)

---

## Testing

1. Upload a PDF document
2. Ask document-related questions
3. Verify answers are relevant
4. Test multiple queries on the same document

---

## Common Issues

Missing dependencies:
pip install -r requirements.txt

Invalid API key:
Check the .env file and Hugging Face access permissions

Vector database issues:
Delete the vector_db folder and restart the application

Port already in use:
Change the port number in run_app.py

---

## Technologies Used

- Python 3.11
- FastAPI
- Hugging Face Transformers
- FAISS
- SQLite
- HTML, CSS, JavaScript
- PyPDF2

---

## Future Improvements

- Support for additional document formats
- User authentication
- Multi-document conversation memory
- Multi-language support
- Domain-specific fine-tuning

---

## License

This project is intended for educational and academic use.

---

Developed for the Computational Intelligence Course By Hamza Ahmad
