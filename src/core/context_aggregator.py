import os
from typing import List, Dict, Any

try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    HAS_RAG = True
except ImportError:
    HAS_RAG = False

class ContextAggregator:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        
    def get_supported_files(self) -> List[str]:
        """
        Recursively finds all source code files that need scanning.
        Filters out common unnecessary directories like node_modules and venv.
        """
        valid_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.json'}
        file_paths = []
        
        if not os.path.isdir(self.repo_path):
            return []
            
        for root, _, files in os.walk(self.repo_path):
            # Skip common hidden or dependency folders
            if any(skip in root for skip in ['.git', 'node_modules', 'venv', '__pycache__']):
                continue
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in valid_extensions:
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def extract_context(self) -> Dict[str, str]:
        """
        Extracts the content of all supported source code files.
        Returns a mapping of filepath -> file contents.
        """
        files = self.get_supported_files()
        context_data = {}
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    context_data[file] = f.read()
            except Exception as e:
                print(f"Aggregator Warning: Could not read {file}. Error: {e}")
        return context_data

    def build_vector_store(self, files_dict: Dict[str, str]) -> Any:
        """
        Chunks the extracted files and embeds them into a ChromaDB instance for semantic RAG auditing.
        """
        if not HAS_RAG:
            print("Warning: RAG packages not installed. Returning None.")
            return None
            
        docs = []
        for path, content in files_dict.items():
            if content.strip():
                docs.append(Document(page_content=content, metadata={"source": path}))
                
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        return vectorstore

if __name__ == "__main__":
    # Test execution
    aggregator = ContextAggregator("./")
    files = aggregator.get_supported_files()
    print(f"Found {len(files)} files to scan.")
