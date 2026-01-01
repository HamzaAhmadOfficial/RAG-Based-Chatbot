"""
PDF Handler Module
Handles PDF text extraction and chunking for RAG system
"""

import PyPDF2
from typing import List, Dict
import re


class PDFHandler:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF handler with chunking parameters
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing full text and metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                # Extract text from all pages
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    page_texts.append({
                        'page_number': page_num + 1,
                        'text': page_text
                    })
                    full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                return {
                    'full_text': full_text,
                    'page_texts': page_texts,
                    'metadata': metadata
                }
        
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of text chunks with metadata
        """
        # Clean the text
        text = self.clean_text(text)
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                last_period = chunk.rfind('.')
                last_question = chunk.rfind('?')
                last_exclamation = chunk.rfind('!')
                
                sentence_end = max(last_period, last_question, last_exclamation)
                
                if sentence_end > self.chunk_size // 2:  # Only break if we're past halfway
                    chunk = chunk[:sentence_end + 1]
                    end = start + sentence_end + 1
            
            # Create chunk with metadata
            chunk_data = {
                'text': chunk.strip(),
                'start_pos': start,
                'end_pos': end,
                'chunk_id': len(chunks)
            }
            
            # Add additional metadata if provided
            if metadata:
                chunk_data.update(metadata)
            
            chunks.append(chunk_data)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text chunks with metadata
        """
        # Extract text
        extraction_result = self.extract_text_from_pdf(pdf_path)
        
        # Chunk the full text
        chunks = self.chunk_text(
            extraction_result['full_text'],
            metadata={
                'source': pdf_path,
                'num_pages': extraction_result['metadata']['num_pages'],
                'title': extraction_result['metadata']['title']
            }
        )
        
        return chunks


if __name__ == "__main__":
    # Test the PDF handler
    handler = PDFHandler()
    
    # Example usage
    print("PDF Handler initialized successfully!")
    print(f"Chunk size: {handler.chunk_size}")
    print(f"Chunk overlap: {handler.chunk_overlap}")
