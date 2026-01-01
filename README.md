# RAG Chatbot - Document Q&A System

A powerful Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents, ask questions, and receive accurate, context-aware answers powered by Hugging Face AI models.

![RAG Chatbot](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.11-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

## ✨ Features

- 📄 **PDF Upload & Processing**: Upload PDF documents with automatic text extraction and chunking
- 🔍 **Semantic Search**: FAISS vector database for fast, efficient document retrieval
- 🤖 **AI-Powered Answers**: Hugging Face Mistral-7B for natural language generation
- 💬 **Chat Interface**: Modern, responsive web interface with real-time interactions
- 📚 **Source Citations**: Answers include references to source documents
- 💾 **Chat History**: SQLite database for conversation persistence
- 🎨 **Premium UI**: Dark theme with glassmorphism and smooth animations
- 🪟 **Windows Compatible**: No C++ build tools required

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI    │────▶│  Vector DB  │
│  (HTML/CSS/ │     │   Backend    │     │   (FAISS)   │
│     JS)     │◀────│              │◀────│             │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Hugging Face │
                    │     API      │
                    │ (Embeddings  │
                    │   & LLM)     │
                    └──────────────┘
```

## 📋 Prerequisites

- Python 3.11 or higher
- Hugging Face API key ([Get one here](https://huggingface.co/settings/tokens))
- 4GB+ RAM recommended

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
cd "d:/7TH SEMESTER/Computational Intelligence/Sem Project"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Edit the `.env` file and add your Hugging Face API key:

```env
HUGGINGFACE_API_KEY=your_actual_api_key_here
```

### 4. Run First-Time Setup

```bash
python first_run.py
```

This will:
- Create necessary directories
- Verify dependencies
- Check environment configuration

### 5. Start the Application

```bash
python run_app.py
```

The application will:
- Start the FastAPI server on `http://localhost:8000`
- Automatically open your browser
- Be ready to accept PDF uploads

## 📖 Usage

### Uploading Documents

1. Click the **"Choose File"** button or drag-and-drop a PDF
2. Wait for processing (you'll see a success message with chunk count)
3. The chat interface will become active

### Asking Questions

1. Type your question in the input field
2. Press **Enter** or click the send button
3. The AI will retrieve relevant context and generate an answer
4. View source citations below each answer

### Managing Data

- **Clear Database**: Click the "Clear" button to remove all documents and chat history
- **Upload New Document**: Upload additional PDFs to expand the knowledge base

## 🗂️ Project Structure

```
SEMESTER PROJECT/
├── frontend/                 # Web interface
│   ├── index.html           # Main HTML page
│   ├── style.css            # Styling with animations
│   └── script.js            # Client-side logic
├── vector_db/               # ChromaDB storage (auto-generated)
├── uploads/                 # Uploaded PDF files (auto-generated)
├── chat_bot.py              # RAG implementation
├── database.py              # Chat history management
├── main.py                  # FastAPI application
├── pdf_handler.py           # PDF processing
├── vector_db.py             # Vector database operations
├── run_app.py               # Application launcher
├── first_run.py             # Setup script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── .env                     # Environment variables
└── README.md                # This file
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend interface |
| `/upload-pdf` | POST | Upload and process PDF |
| `/ask` | POST | Ask question about documents |
| `/history` | GET | Retrieve chat history |
| `/documents` | GET | List uploaded documents |
| `/clear` | DELETE | Clear database |
| `/health` | GET | Health check |

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t rag-chatbot .
```

### Run Container

```bash
docker run -p 8000:8000 -e HUGGINGFACE_API_KEY=your_key rag-chatbot
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_API_KEY` | Hugging Face API key | Required |
| `DATABASE_PATH` | SQLite database path | `chat_history.db` |
| `VECTOR_DB_PATH` | ChromaDB storage path | `./vector_db` |

### Customization

**Change LLM Model** (in `chat_bot.py`):
```python
self.llm_model = "mistralai/Mistral-7B-Instruct-v0.2"
# Alternative: "google/flan-t5-large" for faster responses
```

**Adjust Chunk Size** (in `main.py`):
```python
pdf_handler = PDFHandler(chunk_size=1000, chunk_overlap=200)
```

**Modify Context Documents** (in `chat_bot.py`):
```python
result = chatbot.answer_question(question, n_context_docs=3)
```

## 🧪 Testing

1. Upload a sample PDF (e.g., research paper, manual, policy document)
2. Ask specific questions:
   - "What is the main topic of this document?"
   - "Summarize the key points"
   - "What does it say about [specific topic]?"
3. Verify source citations match the content

## 🐛 Troubleshooting

### "No module named 'X'" Error
```bash
pip install -r requirements.txt
```

### Hugging Face API Errors
- Verify your API key is correct in `.env`
- Check your API quota at https://huggingface.co
- Some models may require approval - use alternatives if needed

### FAISS/Vector Database Issues
```bash
# Clear vector database
python -c "import shutil; shutil.rmtree('vector_db', ignore_errors=True)"
```

### Port Already in Use
```bash
# Change port in run_app.py
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

## 📚 Technologies Used

- **Backend**: FastAPI, Python 3.11
- **AI/ML**: Hugging Face Transformers (Mistral-7B, sentence-transformers)
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **PDF Processing**: PyPDF2

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add support for other document formats (DOCX, TXT)
- Implement user authentication
- Add conversation memory for multi-turn dialogues
- Support for multiple languages
- Fine-tune models for specific domains

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Hugging Face for providing free AI model APIs
- Facebook AI Research for FAISS vector database
- FastAPI for the excellent web framework

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Verify your environment configuration

---

**Built with ❤️ for Computational Intelligence Course**
