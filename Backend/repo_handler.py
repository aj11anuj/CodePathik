import os
import re
import tempfile
import shutil
import zipfile
import requests
from typing import Any, Dict, Union 

def build_file_tree(root_dir: str) -> Dict[str, Any]:  
    """Build a nested dictionary representing the file tree."""
    tree = {}
    for dirpath, _, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        parts = rel_path.split(os.sep)
        current = tree

        for part in parts:
            if part == ".":
                continue
            current = current.setdefault(part, {})

        for file in filenames:
            current[file] = None
    return tree

async def fetch_file_content(repo_url: str, file_path: str) -> Dict[str, Any]:
    """Fetch raw content of a file from GitHub"""
    try:
        pattern = r"https:\/\/github\.com\/([\w\-\.]+)\/([\w\-\.]+)"
        match = re.match(pattern, repo_url.strip())
        if not match:
            return {"error": "Invalid GitHub URL"}
        
        user, repo = match.groups()
        
        # Get default branch first
        repo_info = requests.get(f"https://api.github.com/repos/{user}/{repo}")
        if repo_info.status_code != 200:
            return {"error": "Cannot fetch repo info"}
            
        default_branch = repo_info.json().get("default_branch", "main")
        
        # Get file content using the Git Data API
        content_url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}?ref={default_branch}"
        response = requests.get(content_url)
        
        if response.status_code != 200:
            return {"error": f"File not found (HTTP {response.status_code})"}
        
        content = response.json().get("content")
        if not content:
            return {"error": "No content available"}
            
        import base64
        return {
            "content": base64.b64decode(content).decode("utf-8"),
            "language": file_path.split(".")[-1]  # Simple file extension detection
        }
        
    except Exception as e:
        return {"error": f"Failed to fetch file: {str(e)}"}

async def process_github_repo(url: str) -> Dict[str, Union[str, int, Dict]]:  # ✅ Fix here
    """Process a GitHub repository and return its metadata and structure."""
    if not (match := re.match(r"https:\/\/github\.com\/([\w\-\.]+)\/([\w\-\.]+)", url.strip())):
        return {"error": "Invalid GitHub repo URL."}

    user, repo = match.groups()
    repo_api = f"https://api.github.com/repos/{user}/{repo}"
    
    if (meta_res := requests.get(repo_api)).status_code != 200:
        return {"error": "GitHub repo not found or API rate limited."}
    
    meta_data = meta_res.json()
    default_branch = meta_data.get("default_branch", "main")
    zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/{default_branch}.zip"

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            zip_path = os.path.join(temp_dir, "repo.zip")
            if (r := requests.get(zip_url)).status_code != 200:
                return {"error": f"Failed to download ZIP from {zip_url}"}

            with open(zip_path, "wb") as f:
                f.write(r.content)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_folder = os.path.join(temp_dir, f"{repo}-{default_branch}")
            if not os.path.exists(extracted_folder):
                return {"error": "Unzipped repo folder not found."}

            return {
                "name": meta_data["name"],
                "description": meta_data.get("description", "No description."),
                "stars": meta_data.get("stargazers_count", 0),
                "language": meta_data.get("language", "Unknown"),
                "file_tree": build_file_tree(extracted_folder)
            }

        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}
