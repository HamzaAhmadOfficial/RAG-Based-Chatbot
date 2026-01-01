"""
Vector Database Module
Handles vector storage and similarity search using FAISS and Hugging Face embeddings
"""

import faiss
import numpy as np
import os
import pickle
from typing import List, Dict
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VectorDatabase:
    def __init__(self, persist_directory: str = "./vector_db", api_key: str = None):
        """
        Initialize Vector Database with FAISS and Hugging Face embeddings
        
        Args:
            persist_directory: Directory to persist the database
            api_key: Hugging Face API key
        """
        self.persist_directory = persist_directory
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        
        # Validate API key
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found. Please set it in .env file")
        
        print(f"API Key loaded: {self.api_key[:10]}..." if self.api_key else "No API key")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Hugging Face embedding model
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize Hugging Face Inference Client
        self.client = InferenceClient(token=self.api_key)
        
        # FAISS index
        self.index = None
        self.documents = []
        self.metadatas = []
        self.collection_name = None
        
        # File paths
        self.index_path = os.path.join(persist_directory, "faiss.index")
        self.docs_path = os.path.join(persist_directory, "documents.pkl")
        self.meta_path = os.path.join(persist_directory, "metadata.pkl")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using Hugging Face API
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Use feature extraction with the inference client
            embedding = self.client.feature_extraction(
                text,
                model=self.embedding_model
            )
            
            # Handle different response formats
            if isinstance(embedding, list):
                if len(embedding) > 0 and isinstance(embedding[0], list):
                    return embedding[0]  # Nested list
                return embedding
            
            return list(embedding)
        
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
    
    def get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return np.array(embeddings, dtype='float32')
    
    def create_collection(self, collection_name: str = "documents"):
        """
        Create or load a collection
        
        Args:
            collection_name: Name of the collection
        """
        self.collection_name = collection_name
        
        # Try to load existing index
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                with open(self.meta_path, 'rb') as f:
                    self.metadatas = pickle.load(f)
                print(f"Loaded existing collection: {collection_name} with {len(self.documents)} documents")
                return
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
        
        # Create new index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.metadatas = []
        print(f"Created new collection: {collection_name}")
    
    def add_documents(self, chunks: List[Dict], collection_name: str = "documents"):
        """
        Add document chunks to the vector database
        
        Args:
            chunks: List of text chunks with metadata
            collection_name: Name of the collection
        """
        if self.index is None:
            self.create_collection(collection_name)
        
        # Prepare data for insertion
        texts = [chunk['text'] for chunk in chunks]
        
        # Get embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.get_batch_embeddings(texts)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents.extend(texts)
        for chunk in chunks:
            metadata = {
                'source': chunk.get('source', 'unknown'),
                'chunk_id': str(chunk.get('chunk_id', 0)),
                'title': chunk.get('title', 'Unknown')
            }
            self.metadatas.append(metadata)
        
        # Save to disk
        self._save()
        
        print(f"Added {len(texts)} documents to collection")
    
    def query(self, query_text: str, n_results: int = 5) -> Dict:
        """
        Query the vector database for similar documents
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            Query results with documents and metadata
        """
        if self.index is None or len(self.documents) == 0:
            return {
                'documents': [],
                'metadatas': [],
                'distances': []
            }
        
        # Get query embedding
        query_embedding = np.array([self.get_embedding(query_text)], dtype='float32')
        
        # Search
        n_results = min(n_results, len(self.documents))
        distances, indices = self.index.search(query_embedding, n_results)
        
        # Format results
        results_docs = [self.documents[i] for i in indices[0]]
        results_meta = [self.metadatas[i] for i in indices[0]]
        results_dist = distances[0].tolist()
        
        formatted_results = {
            'documents': results_docs,
            'metadatas': results_meta,
            'distances': results_dist
        }
        
        return formatted_results
    
    def delete_collection(self, collection_name: str = "documents"):
        """
        Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.docs_path):
                os.remove(self.docs_path)
            if os.path.exists(self.meta_path):
                os.remove(self.meta_path)
            
            self.index = None
            self.documents = []
            self.metadatas = []
            self.collection_name = None
            print(f"Deleted collection: {collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the current collection
        
        Returns:
            Number of documents
        """
        return len(self.documents)
    
    def reset_database(self):
        """
        Reset the entire database
        """
        self.delete_collection()
        print("Database reset successfully")
    
    def _save(self):
        """Save index and data to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            with open(self.meta_path, 'wb') as f:
                pickle.dump(self.metadatas, f)
        except Exception as e:
            print(f"Error saving index: {e}")


if __name__ == "__main__":
    # Test the vector database
    print("Vector Database initialized successfully!")
    print("Using FAISS with Hugging Face embeddings")
