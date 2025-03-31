import os
import json
import re
from google import genai
from dotenv import load_dotenv

from .utils.data import resume_text, job_description
from .utils.prompts import get_resume_analysis_prompt, get_cover_letter_prompt



load_dotenv()

class AIClient:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('MODEL_API'))
        self.model = os.getenv('MODEL_NAME')

    def generate_response(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text


class ResumeGeneratorWithAnalysis:
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def generate_resume(self, job_description, resume_text):
        prompt = get_resume_analysis_prompt(job_description, resume_text)
        response_text = self.ai_client.generate_response(prompt)

        if not response_text:
            print("AI response is empty or invalid.")
            return None

        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            print("No valid JSON found in AI response.")
            return None

        json_string = json_match.group(0) 

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from AI response: {e}")
            return None


class CoverLetterGenerator:
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def generator_cover_letter(self, job_description, resume_text):
        prompt = get_cover_letter_prompt(job_description, resume_text)
        return self.ai_client.generate_response(prompt)