import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

async def analyze_with_together(repo_data: Dict[str, Any], analyze_code: bool = False) -> Dict[str, Any]:
    """
    Analyze repository using Together.ai's Mixtral 8x7B
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    # Dynamic prompt based on analysis type
    prompt = build_analysis_prompt(repo_data, analyze_code)
    
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json={
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior engineer analyzing GitHub repositories."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            },
            timeout=15
        )
        response.raise_for_status()
        return parse_llm_response(response.json(), analyze_code)
    
    except Exception as e:
        return {"error": str(e)}

def build_analysis_prompt(repo_data: Dict[str, Any], analyze_code: bool) -> str:
    """Build dynamic prompt for different analysis types"""
    base_prompt = f"""
    Repository: {repo_data['name']}
    Description: {repo_data.get('description', 'None')}
    Language: {repo_data.get('language', 'Unknown')}
    File Structure: {repo_data['file_tree']}
    """
    
    if analyze_code:
        return f"""
        {base_prompt}
        Analyze THIS CODE from {repo_data['current_file']}:
        ```{repo_data['language']}
        {repo_data['file_content']}
        ```
        
        Provide:
        1. Purpose of this file
        2. Key functions/classes
        3. Dependencies
        4. Any security/performance concerns
        """
    else:
        return f"""
        {base_prompt}
        Provide repository-level analysis:
        1. Project purpose (1 sentence)
        2. Key components
        3. Architectural patterns
        4. Getting started guide
        5. Code quality assessment
        """

def parse_llm_response(response_data: Dict[str, Any], analyze_code: bool) -> Dict[str, Any]:
    """Structure the LLM response into our format"""
    content = response_data['choices'][0]['message']['content']
    
    # Standardized response format
    if analyze_code:
        return {
            "analysis": {
                "purpose": extract_section(content, "Purpose"),
                "components": extract_list_items(content, "Key functions/classes"),
                "code_insights": content
            }
        }
    else:
        return {
            "overview": extract_section(content, "Project purpose"),
            "detailed": content,
            "architecture": extract_section(content, "Architectural patterns")
        }

def extract_section(text: str, title: str) -> str:
    """Helper to extract sections from LLM response"""
    start_idx = text.find(title)
    if start_idx == -1:
        return ""
    end_idx = text.find("\n\n", start_idx)
    return text[start_idx:end_idx if end_idx != -1 else len(text)]

def extract_list_items(text: str, section_title: str) -> List[str]:
    """Helper to extract bullet points from LLM response"""
    section = extract_section(text, section_title)
    return [line.strip("- ").strip() for line in section.split("\n") if line.strip()]