import os
import json
import re
from google import genai
from dotenv import load_dotenv

from utils.data import resume_text, job_description
from utils.prompts import get_resume_analysis_prompt, get_cover_letter_prompt



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

        # Try extracting JSON using regex to ensure we only process valid JSON
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            print("No valid JSON found in AI response.")
            return None

        json_string = json_match.group(0)  # Extract matched JSON part

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
    


if __name__ == "__main__":
    ai_client = AIClient()

    resume_generator = ResumeGeneratorWithAnalysis(ai_client)
    cover_letter_generator = CoverLetterGenerator(ai_client)

    resume_output = resume_generator.generate_resume(job_description, resume_text)

    if resume_output:
        tailored_resume = resume_output.get('resume', '')
        resume_analysis = resume_output.get('analysis', '')
    else:
        tailored_resume, resume_analysis = None, None

    tailored_cover_letter = cover_letter_generator.generate_cover_letter(job_description, resume_text)

    print("Generated Resume:", tailored_resume)
    print("Resume Analysis:", resume_analysis)
    print("Generated Cover Letter:", tailored_cover_letter)