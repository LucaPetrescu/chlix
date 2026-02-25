#!/usr/bin/env python3

import sys
import os
import argparse
from pathlib import Path
from chroma.CodebaseIndexer import CodebaseIndexer
from chroma.CodebaseQuery import CodebaseQuery
from chroma.ChromaDBManager import ChromaDBManager


def extract_repo_name(repo_path: str) -> str:
    normalized_path = os.path.normpath(repo_path)
    return os.path.basename(normalized_path)


def handle_index(args):
    repo_path = args.path
    
    if not os.path.exists(repo_path):
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)
    
    if not os.path.isdir(repo_path):
        print(f"Error: Path is not a directory: {repo_path}")
        sys.exit(1)
    
    collection_name = extract_repo_name(repo_path)
    
    print(f"Repository: {repo_path}")
    print(f"Collection: {collection_name}")
    print()
    
    try:
        indexer = CodebaseIndexer(collection_name=collection_name)
        indexer.index_directory(repo_path)
        
        stats = indexer.get_stats()
        print()
        print(f"Collection Name: {stats['collection_name']}")
        print(f"Total Chunks: {stats['total_chunks']}")
        print(f"Successfully indexed '{collection_name}'")
        
    except Exception as e:
        print(f"Error during indexing: {str(e)}")
        sys.exit(1)


def handle_search(args):
    collection_name = args.collection
    query_text = args.query
    n_results = args.n_results
    
    try:
        query = CodebaseQuery(collection_name=collection_name)
        results = query.search(query_text, n_results=n_results)
        
        if not results:
            print(f"No results found for: {query_text}")
            return
        
        print(f"Found {len(results)} results for: {query_text}\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}: {result['file_path']}")
            print(f"Lines {result['start_line']}-{result['end_line']}")
            if result.get('relevance_score'):
                print(f"Relevance: {result['relevance_score']:.2f}")
            print()
            print(result['content'])
            print("\n" + "-" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Codebase indexing and query tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    index_parser = subparsers.add_parser("index", help="Index a codebase")
    index_parser.add_argument("path", type=str, help="Path to the codebase")
    
    search_parser = subparsers.add_parser("search", help="Search the indexed codebase")
    search_parser.add_argument("collection", type=str, help="Collection name")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--n-results", type=int, default=5, help="Number of results")
    
    list_parser = subparsers.add_parser("list", help="List all collections")
    
    info_parser = subparsers.add_parser("info", help="Get info about a collection")
    info_parser.add_argument("collection", type=str, help="Collection name")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a collection")
    delete_parser.add_argument("collection", type=str, help="Collection name")
    delete_parser.add_argument("--confirm", action="store_true", help="Confirm deletion")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "index":
        handle_index(args)
    
    elif args.command == "search":
        handle_search(args)
    
    elif args.command == "list":
        try:
            db_manager = ChromaDBManager()
            collections = db_manager.list_collections()
            
            if not collections:
                print("No collections found.")
                print("Index a codebase with: chlix index /path/to/repo")
            else:
                print(f"Available collections ({len(collections)}):\n")
                for col in collections:
                    print(f"  - {col['name']} ({col['count']} chunks)")
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Make sure ChromaDB is running: ./run-chromadb.sh")
            sys.exit(1)
    
    elif args.command == "info":
        try:
            db_manager = ChromaDBManager()
            info = db_manager.get_collection_info(args.collection)
            
            print(f"Collection: {info['name']}")
            print(f"Total chunks: {info['count']}")
            
            if info['sample_metadata']:
                print(f"\nSample metadata:")
                for key, value in info['sample_metadata'].items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error: {str(e)}")
            print("List available collections with: chlix list")
            sys.exit(1)
    
    elif args.command == "delete":
        if not args.confirm:
            print(f"Are you sure you want to delete collection '{args.collection}'?")
            print("Add --confirm to proceed")
            sys.exit(0)
        
        try:
            db_manager = ChromaDBManager()
            db_manager.delete_collection(args.collection)
            print(f"Deleted collection: {args.collection}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
