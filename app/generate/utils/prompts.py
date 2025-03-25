# utils/prompts.py

def get_resume_analysis_prompt(job_description, resume_text):
    return f"""
    You are an AI assistant specializing in extracting and structuring resume information with optimization.
    Your task is to analyze the provided job description and resume accordingly, containing the key sections of a resume.
    Based on the job description and tailored resume by you,
    provide the probability of user getting interview call based on tailored resume and job description
    Percentage of matched keywords from the job description that are in tailored resume
    All the keywords found in the job description
    provide 3 specific recommendations to improve the candidate's chances of getting an interview call,
    and then output a JSON object

    **Output Format:**

    {{
    "resume": {{
        "name": "Candidate's Full Name",
        "contact_details": "Phone number, Email, LinkedIn profile URL (if available)",
        "summary": "A concise summary of the candidate's skills and experience",
        "skills": ["Skill 1", "Skill 2", "Skill 3", ...],
        "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "dates": "Start Date - End Date",
            "description": "Detailed description of responsibilities and achievements"
        }},
        ...
        ],
        "education": [
        {{
            "degree": "Degree Name",
            "university": "University Name",
            "dates": "Graduation Date"
        }},
        ...
        ],
        "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description of the project"
        }},
        ...
        ],
        "certifications": ["Certification 1", "Certification 2", ...]
    }},
    "analysis": {{
        "success_probability": "A percentage (0-100) indicating the likelihood of getting hired",
        "keyword_match_percentage": "Percentage of matched keywords from the job description",
        "keywords_found": ["Keyword1", "Keyword2", ...],
        "recommendations": "Specific recommendations to improve the resume for this job"
    }}
    }}

    **Important Guidelines:**
    * Do NOT include any information that is not already present in the original resume.
    * Extract information accurately and concisely from the resume.
    * Ensure the output is a STRICTLY VALID JSON response.
    * Use double quotes for all strings.

    **Job Description:**
    {job_description}

    **Original Resume:**
    {resume_text}

    **JSON Output:**
    """


def get_cover_letter_prompt(job_description, resume_text):
    return f"""
    You are a professional cover letter writer. Your task is to write a compelling cover letter
    for a job application, tailored to the following job description and the candidate's resume.

    **Important Guidelines:**
    * Focus on the candidate's existing skills and experience as presented in the resume.
    * Highlight how the candidate's qualifications align with the job description.
    * Maintain a professional and enthusiastic tone.
    * Keep the cover letter concise and focused (3-4 paragraphs).
    * Address the cover letter to "Hiring Manager" unless a specific name is provided.

    **Job Description:**
    {job_description}

    **Candidate's Resume:**
    {resume_text}

    **Cover Letter:**
    """


def extract_user_details_from_resume(resume_text):
    return f"""
    Can you extract resume details from my resume and make it into a json format like 'name': name, 'contact': 'phone': phone, 'email': email, skills: all skills in list, education: .....
    so on like that extract all fields and put them in json format and output the JSON form of my resume 
    and here is the text of my resume {resume_text}

    **Important Guidelines:**
    * Do NOT include any information that is not already present in the original resume.
    * Extract information accurately and concisely from the resume.
    * Ensure the output is a STRICTLY VALID JSON response.
    * Use double quotes for all strings.
    """
