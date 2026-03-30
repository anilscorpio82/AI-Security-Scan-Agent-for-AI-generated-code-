import os
from typing import List, Dict

class ContextAggregator:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        
    def get_supported_files(self) -> List[str]:
        """
        Recursively finds all source code files that need scanning.
        Filters out common unnecessary directories like node_modules and venv.
        """
        valid_extensions = {'.py', '.js', '.ts', '.go', '.java', '.json'}
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

if __name__ == "__main__":
    # Test execution
    aggregator = ContextAggregator("./")
    files = aggregator.get_supported_files()
    print(f"Found {len(files)} files to scan.")
