import chromadb
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class CodebaseQuery:
    """Query the indexed codebase."""
    
    def __init__(self, collection_name: str = "codebase"):
        """Initialize the query interface."""
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            raise Exception(f"Collection '{collection_name}' not found. Please index your codebase first.")

    def search(self, query: str, n_results: int = 5, file_type: str = None) -> List[Dict]:
        """Search for relevant code chunks."""
        where = None
        if file_type:
            where = {"file_type": file_type}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results else None
                
                formatted_results.append({
                    'content': doc,
                    'file_path': metadata.get('file_path'),
                    'start_line': metadata.get('start_line'),
                    'end_line': metadata.get('end_line'),
                    'file_type': metadata.get('file_type'),
                    'relevance_score': 1 - distance if distance else None
                })
        
        return formatted_results 

    def get_context_for_llm(self, query: str, n_results: int = 5, max_tokens: int = 4000) -> str:
        """Get formatted context for LLM consumption."""
        results = self.search(query, n_results)
        
        context = "# Relevant Code Context\n\n"
        current_tokens = 0
        
        for i, result in enumerate(results, 1):
            chunk_text = f"## File: {result['file_path']} (Lines {result['start_line']}-{result['end_line']})\n"
            chunk_text += f"{result['file_type'].lstrip('.')}\n"
            chunk_text += result['content']
            chunk_text += "\n"

            chunk_tokens = len(chunk_text) // 4
            
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            context += chunk_text
            current_tokens += chunk_tokens
        
        return context

    def search_by_file(self, file_path: str) -> List[Dict]:
        """Get all chunks from a specific file."""
        results = self.collection.get(
            where={"file_path": file_path}
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                metadata = results['metadatas'][i]
                formatted_results.append({
                    'content': doc,
                    'file_path': metadata.get('file_path'),
                    'start_line': metadata.get('start_line'),
                    'end_line': metadata.get('end_line'),
                })
        
        return sorted(formatted_results, key=lambda x: x['start_line'])
