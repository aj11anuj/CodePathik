# CodePathik 🧭

This interactive web tool helps developers explore and understand GitHub repositories more effectively. By combining a file tree visualisation with LLM-powered analysis, it enables users to grasp project structure, purpose, and individual file functionality without manually reading through the codebase.

## Features

- Paste a GitHub repo URL to visualise its file structure.
- Get project architecture and overview of the project.
- Analyse any file in the repository to understand its purpose, components, and functionality.
- It also provides insights into areas where you can contribute to the project. 
- FastAPI backend with AI integration (8x more powerful than Mistral 7B).

## File Overview

| File                  | Description |
|-----------------------|-------------|
| `main.py`             | FastAPI app with CORS and three API routes for analysis |
| `repo_handler.py`     | Handles GitHub API interactions and builds repo file tree |
| `llm_integration.py`  | Sends repo/code data to Together.ai and parses the response |
| `index.html`          | Frontend UI with tree view and analysis controls |
| `requirements.txt`    | Python dependencies for the backend |

## Requirements

- Python 3.10+
- GitHub Personal Access Token (`GITHUB_PAT`)
- Together.ai API key (`TOGETHER_API_KEY`)
- FastAPI (Backend framework)
- Uvicorn (Server for FastAPI)
- Requests (Module for handling requests)
- Python-dotenv (for .env file)
- Frontend: Vercel (or any static host)
- Backend: Render (or any FastAPI-compatible host)

## How to Use

-  1. Clone the repo and install dependencies
   ```bash
   pip install -r requirements.txt
   ```
-  2. Create .env file
   ```bash
   TOGETHER_API_KEY=your_together_api_key
   GITHUB_PAT=your_github_pat
   ```
-  3. Run the backend
   ```bash
   uvicorn main:app --reload
   ```
-  4. Run frontend on browser and check API calls in Swagger
   ```bash
   Access Swagger at /docs route at port 8000 or Localhost
   ```

## Sample Output
![Screenshot (1232)](https://github.com/user-attachments/assets/2b1df4c1-02f3-48a0-8061-c3f0360a2ebb)

