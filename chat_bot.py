"""
Chat Bot Module
Implements RAG (Retrieval-Augmented Generation) using Hugging Face models
"""

import os
from typing import List, Dict
from vector_db import VectorDatabase
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ChatBot:
    def __init__(self, vector_db: VectorDatabase, api_key: str = None):
        """
        Initialize ChatBot with vector database and Hugging Face API
        
        Args:
            vector_db: VectorDatabase instance
            api_key: Hugging Face API key
        """
        self.vector_db = vector_db
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize Hugging Face Inference Client
        self.client = InferenceClient(token=self.api_key)
        
        # Llama 3 is supported on the new Serverless Inference API
        self.llm_model = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    def generate_response(self, prompt: str, max_length: int = 500) -> str:
        """
        Generate response using Hugging Face LLM
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of response
            
        Returns:
            Generated text
        """
        try:
            # Use chat_completion for Llama 3
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.llm_model,
                max_tokens=max_length,
                temperature=0.7,
                top_p=0.95
            )
            
            # Extract the generated text
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            elif isinstance(response, dict):
                return response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            else:
                return str(response).strip()
        
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def create_rag_prompt(self, question: str, context_docs: List[str]) -> str:
        """
        Create RAG prompt with context
        
        Args:
            question: User's question
            context_docs: Retrieved context documents
            
        Returns:
            Formatted prompt
        """
        # Combine context documents
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        # Create prompt for chat completion
        prompt = f"""You are a helpful AI assistant. Answer the question based ONLY on the provided context. If the answer cannot be found in the context, say "I don't have enough information to answer this question based on the provided documents."

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context above."""
        
        return prompt
    
    def answer_question(self, question: str, n_context_docs: int = 3) -> Dict:
        """
        Answer question using RAG
        
        Args:
            question: User's question
            n_context_docs: Number of context documents to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Retrieve relevant context from vector database
            search_results = self.vector_db.query(question, n_results=n_context_docs)
            
            if not search_results['documents']:
                return {
                    'answer': "No documents found in the database. Please upload a PDF first.",
                    'sources': []
                }
            
            # Get context documents
            context_docs = search_results['documents']
            
            # Create RAG prompt
            prompt = self.create_rag_prompt(question, context_docs)
            
            # Generate answer
            answer = self.generate_response(prompt, max_length=500)
            
            # Prepare sources
            sources = []
            for i, (doc, metadata) in enumerate(zip(search_results['documents'], 
                                                     search_results['metadatas'])):
                sources.append({
                    'chunk_id': metadata.get('chunk_id', i),
                    'source': metadata.get('source', 'Unknown'),
                    'title': metadata.get('title', 'Unknown'),
                    'text_preview': doc[:200] + "..." if len(doc) > 200 else doc,
                    'relevance_score': 1 - search_results['distances'][i]  # Convert distance to similarity
                })
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': len(context_docs)
            }
        
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'sources': [],
                'error': str(e)
            }
    
    def chat(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Chat with context awareness
        
        Args:
            question: User's question
            conversation_history: Previous conversation messages
            
        Returns:
            Response dictionary
        """
        # For now, just use the basic answer_question
        # Can be extended to include conversation history
        return self.answer_question(question)


if __name__ == "__main__":
    # Test the chatbot
    print("ChatBot initialized successfully!")
    print("Using Hugging Face Mistral-7B for text generation")
