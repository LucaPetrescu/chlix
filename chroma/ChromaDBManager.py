#!/usr/bin/env python3

import chromadb
from typing import List, Dict

class ChromaDBManager:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.client = None
    
    def connect(self):
        try:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ChromaDB at {self.host}:{self.port}. Error: {str(e)}")
    
    def list_collections(self) -> List[Dict[str, any]]:
        if not self.client:
            self.connect()
        
        collections = self.client.list_collections()
        
        result = []
        for col in collections:
            result.append({
                'name': col.name,
                'count': col.count()
            })
        
        return result
    
    def get_collection_info(self, collection_name: str) -> Dict[str, any]:
        if not self.client:
            self.connect()
        
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            info = {
                'name': collection_name,
                'count': count,
                'sample_metadata': None
            }
            
            if count > 0:
                sample = collection.get(limit=1, include=["metadatas"])
                if sample['metadatas']:
                    info['sample_metadata'] = sample['metadatas'][0]
            
            return info
            
        except Exception as e:
            raise ValueError(f"Collection '{collection_name}' not found")
    
    def delete_collection(self, collection_name: str) -> bool:
        if not self.client:
            self.connect()
        
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete collection '{collection_name}': {str(e)}")
    
    def collection_exists(self, collection_name: str) -> bool:
        if not self.client:
            self.connect()
        
        try:
            self.client.get_collection(name=collection_name)
            return True
        except:
            return False
