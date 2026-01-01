"""
Application Launcher
Runs the FastAPI application and opens browser
"""

import uvicorn
import webbrowser
import time
from threading import Timer


def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Chatbot Application")
    print("=" * 60)
    print("\nStarting server...")
    print("Server will be available at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in background
    Timer(2, open_browser).start()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
