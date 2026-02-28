import chromadb
import hashlib
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pathlib import Path

class CodebaseIndexer:
    def __init__(self, collection_name="codebase"):
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        print(f"📦 Using collection: '{collection_name}'")

    def should_index_file(self, file_path: str) -> bool:
        """Determine if a file should be indexed."""

        skip_dirs = {
            'node_modules', '.git', 'dist', 'build', '__pycache__',
            '.venv', 'venv', 'coverage', '.pytest_cache', 'chroma_db'
        }

        allowed_extensions = {
            '.py', '.ts', '.js', '.tsx', '.jsx', '.mjs', '.cjs',
            '.vue', '.svelte', '.css', '.scss', '.sass', '.less',
            '.html', '.htm', '.md', '.txt', '.feature',
            '.yml', '.yaml', '.json', '.env.example', '.env.sample',
            '.sh', '.bash', '.tf', '.tfvars', '.sql',
            '.graphql', '.gql', '.rs', '.go', '.java', '.kt', '.kts',
            '.rb', '.php', '.ex', '.exs', '.cs', '.vb', '.fs', '.fsi'
        }

        path_parts = Path(file_path).parts
        if any(skip_dir in path_parts for skip_dir in skip_dirs):
            return False

        return Path(file_path).suffix in allowed_extensions

    def chunk_code(self, content: str, file_path: str, chunk_size: int = 1000) -> List[Dict]:
        """Chunk code into smaller chunks."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        start_line = 1

        for i, line in enumerate(lines, 1):
            line_size = len(line)
            
            if current_size + line_size > chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'file_path': file_path,
                    'start_line': start_line,
                    'end_line': i - 1,
                    'chunk_id': f"{file_path}:{start_line}-{i-1}"
                })
                current_chunk = []
                current_size = 0
                start_line = i
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'file_path': file_path,
                'start_line': start_line,
                'end_line': len(lines),
                'chunk_id': f"{file_path}:{start_line}-{len(lines)}"
            })
        
        return chunks

    def index_file(self, file_path: str, base_path: str):
        """Index a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return
            
            rel_path = os.path.relpath(file_path, base_path)
            
            chunks = self.chunk_code(content, rel_path)
            
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                chunk_hash = hashlib.md5(chunk['chunk_id'].encode()).hexdigest()
                
                documents.append(chunk['text'])
                metadatas.append({
                    'file_path': chunk['file_path'],
                    'start_line': chunk['start_line'],
                    'end_line': chunk['end_line'],
                    'file_type': Path(file_path).suffix,
                })
                ids.append(chunk_hash)
            
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"✓ Indexed: {rel_path} ({len(chunks)} chunks)")
                
        except Exception as e:
            print(f"✗ Error indexing {file_path}: {str(e)}")

    def index_directory(self, directory: str):
        """Index all files in a directory."""
        base_path = os.path.abspath(directory)
        file_count = 0
        
        print(f"Indexing codebase from: {base_path}\n")
        
        for root, dirs, files in os.walk(directory):
            # Skip known build/dep dirs; allow .github and other dot-dirs that may contain config/code
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', 'dist', 'build', '__pycache__', '.venv', 'venv',
                '.git'  # keep .git out to avoid indexing the object store
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self.should_index_file(file_path):
                    self.index_file(file_path, base_path)
                    file_count += 1
        
        print(f"\n✓ Indexing complete! {file_count} files indexed.")
        print(f"Total chunks in database: {self.collection.count()}")

    def get_stats(self):
        """Get statistics about the indexed data."""
        return {
            'total_chunks': self.collection.count(),
            'collection_name': self.collection.name
        }
