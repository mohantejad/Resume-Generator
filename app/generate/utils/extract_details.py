import json
import os
import pdfplumber
import docx
from google import genai
from dotenv import load_dotenv


def extract_user_details_from_resume(resume_text):
    return f"""
    Can you extract resume details from my resume and make it into a JSON format like 'name': name, 'contact': 'phone': phone, 'email': email, skills: all skills in list, education: .....
    so on like that extract all fields and put them in JSON format and output the JSON form of my resume 

    **Important Guidelines:**
    * Do NOT include any information that is not already present in the original resume.
    * Extract information accurately and concisely from the resume.
    * Ensure the output is a STRICTLY VALID JSON response.
    * Use double quotes for all strings.
    * Do NOT wrap the output in markdown-style triple backticks (```json ... ```)
    
    Here is the text of my resume:
    {resume_text}
    """

def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text


def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    return ""

load_dotenv()
client = genai.Client(api_key=os.getenv('MODEL_API'))

def extract_resume_details(prompt: str) -> dict:

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    raw_text = response.candidates[0].content.parts[0].text  # Get text content
    
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        resume_data = json.loads(raw_text)
        return resume_data  
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return None



pdf_path = "/Users/mohantejadharmavarapu/Projects/Resume Generator/backend/app/generate/Mohanteja_Resume.pdf"
resume_text = extract_text_from_pdf(pdf_path)

prompt = extract_user_details_from_resume(resume_text)

resume_details = extract_resume_details(prompt)
