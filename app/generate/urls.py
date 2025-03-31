from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .generator import CoverLetterGenerator, ResumeGeneratorWithAnalysis, AIClient


generate_router = APIRouter()

ai_client = AIClient()
resume_generator = ResumeGeneratorWithAnalysis(ai_client)
cover_letter_generator = CoverLetterGenerator(ai_client)

class ResumeRequest(BaseModel):
    job_description: str
    resume_text: str

from pydantic import BaseModel
from typing import List, Dict

class Experience(BaseModel):
    title: str
    company: str
    dates: str
    description: str

class Education(BaseModel):
    degree: str
    university: str
    dates: str

class Project(BaseModel):
    name: str
    description: str

class ResumeText(BaseModel):
    name: str
    contact_details: str
    summary: str
    skills: List[str]
    experience: List[Experience]
    education: List[Education]
    projects: List[Project]
    certifications: List[str]

class CoverLetterRequest(BaseModel):
    resume_text: ResumeText
    job_description: str


@generate_router.post('/generate-resume')
async def generate_resume(request: ResumeRequest):
    response = resume_generator.generate_resume(request.job_description, request.resume_text)

    if not response:
        raise HTTPException(status_code=400, detail='Failed to generate resume')
    
    return response

@generate_router.post('/generate-cover-letter')
async def generate_resume(request: CoverLetterRequest):
    try:
        cover_letter = cover_letter_generator.generator_cover_letter(request.job_description, request.resume_text)
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))