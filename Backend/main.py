from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from repo_handler import process_github_repo, fetch_file_content
from llm_integration import analyze_with_together
from dotenv import load_dotenv
from healthcheck import router as health_router

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: str

app.include_router(health_router)

@app.post("/analyze")
async def analyze_repo(payload: RepoRequest):
    return await process_github_repo(payload.repo_url)

class CodeAnalysisRequest(BaseModel):
    repo_url: str
    file_path: str  

@app.post("/analyze/repo")
async def analyze_repository(payload: RepoRequest):
    basic_data = await process_github_repo(payload.repo_url)
    if "error" in basic_data:
        return basic_data
    return await analyze_with_together(basic_data)

@app.post("/analyze/code")
async def analyze_code(payload: CodeAnalysisRequest):
    # Get the file content
    file_content = await fetch_file_content(payload.repo_url, payload.file_path)
    if "error" in file_content:
        return file_content
    # Get context
    repo_data = await process_github_repo(payload.repo_url)
    if "error" in repo_data:
        return repo_data
    # Combine for analysis
    analysis_data = {
        **repo_data,
        "current_file": payload.file_path,
        "file_content": file_content
    }
    return await analyze_with_together(analysis_data, analyze_code=True)
