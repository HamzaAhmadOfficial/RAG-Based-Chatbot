"""
First Run Setup Script
Initializes directories and checks dependencies
"""

import os
import sys


def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "vector_db",
        "frontend"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "PyPDF2",
        "chromadb",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is NOT installed")
    
    if missing_packages:
        print("\n" + "=" * 60)
        print("Missing packages detected!")
        print("=" * 60)
        print("\nPlease install missing packages using:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr install all requirements:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("\n" + "=" * 60)
        print("WARNING: .env file not found!")
        print("=" * 60)
        print("\nCreating .env template...")
        
        with open(".env", "w") as f:
            f.write("# Hugging Face API Key\n")
            f.write("HUGGINGFACE_API_KEY=your_huggingface_api_key_here\n")
            f.write("\n# Optional: Database path\n")
            f.write("# DATABASE_PATH=chat_history.db\n")
        
        print("✓ Created .env template")
        print("\nPlease edit .env and add your Hugging Face API key")
        print("Get your API key from: https://huggingface.co/settings/tokens")
        return False
    else:
        print("✓ .env file exists")
        return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("RAG Chatbot - First Run Setup")
    print("=" * 60)
    print()
    
    # Create directories
    print("Creating directories...")
    create_directories()
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    # Check .env file
    print("Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    # Final status
    print("=" * 60)
    if deps_ok and env_ok:
        print("✓ Setup completed successfully!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("python run_app.py")
    else:
        print("⚠ Setup incomplete")
        print("=" * 60)
        print("\nPlease address the issues above before running the application.")
    print()


if __name__ == "__main__":
    main()
