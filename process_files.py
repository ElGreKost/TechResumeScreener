# process_files.py
import os

def read_code_files(repo_path, extensions=None):
    if extensions is None:
        extensions = [
            '.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb',
            '.php', '.html', '.css', '.md', '.txt'
        ]
    code_contents = ""
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        code_contents += f"\n\n### File: {file_path}\n{file_content}"
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
    return code_contents
