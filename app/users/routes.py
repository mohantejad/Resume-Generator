from datetime import datetime
from email.utils import parsedate
import json
import os
from pathlib import Path
import re
import shutil
import uuid
import bcrypt
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.generate.utils.extract_details import extract_resume_details, extract_text
from app.generate.utils.prompts import extract_user_details_from_resume
from app.users.oauth import oauth
from app.users.emails import send_activation_email
from app.users.models import Certification, ContactDetails, Education, Experience, Project, Reference, ResumeFile, SkillMaster, User, UserSkill
from app.users.schemas import ResumeFileResponse, ResumeFileUpdate, UserCreate, UserCreateBase, UserProfileResponse, UserProfileUpdate, UserResponse
from app.users.utils import generate_session_token

load_dotenv()

auth_router = APIRouter()
serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
linkedin = oauth.linkedin


@auth_router.post('/register', response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail='Email already registered')

    hashed_password = bcrypt.hashpw(user_data.password.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        id=uuid.uuid4(),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hashed_password,
        is_active=False
    )

    contact_details = ContactDetails(
        user_id=new_user.id,
        phone=None,
        email=new_user.email,
        github=None,
        linkedin=None,
        portfolio=None,
        location=None
    )
    resume_file = ResumeFile(user_id=new_user.id)  # Empty resume file entry

    # Empty lists for related models
    experiences = [Experience(user_id=new_user.id)]
    education = [Education(user_id=new_user.id)]
    skills = [UserSkill(user_id=new_user.id)]
    # certifications = [Certification(user_id=new_user.id)]
    references = [Reference(user_id=new_user.id)]
    projects = [Project(user_id=new_user.id)]

    db.add(new_user)
    db.add(contact_details)
    # db.add(resume_file)
    # db.add_all(experiences + education + skills + references + projects)

    await db.commit()
    await db.refresh(new_user)

    activation_token = serializer.dumps({'email': user_data.email})
    await send_activation_email(user_data.email, activation_token)

    return new_user


@auth_router.get('/activate')
async def activate_account(token: str, db: AsyncSession = Depends(get_db)):
    try:
        data = serializer.loads(token, max_age=3600)
        email = data.get('email')

        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        if user.is_active:
            return {'message': 'Account already activated'}

        user.is_active = True
        await db.commit()

        return {"message": "Account activated successfully"}

    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Activation link expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid activation token")


redis_client = redis.Redis(host='localhost', port=6379, db=0)


@auth_router.post('/login')
async def login_user(data: UserCreateBase, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == data.email))
    user = result.scalars().first()

    if not user or not user.verify_password(data.password):
        raise HTTPException(
            status_code=401, detail='Invalid email or password')

    session_token = generate_session_token()

    await redis_client.setex(f'session:{session_token}', 86400, str(user.id))

    response.set_cookie(
        key='session_token',
        value=session_token,
        httponly=True,
        secure=True,
        samesite='Lax'
    )

    return {"message": "Login successful"}


@auth_router.post('/logout')
async def logout(response: Response, request: Request):
    session_token = request.cookies.get('session_token')
    if session_token:
        await redis_client.delete(f'session:{session_token}')

        response.delete_cookie('session_token')
        return {'message': 'Logged out successfully'}


@auth_router.get('/user/me', response_model=UserProfileResponse)
async def get_user_details(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid user ID format')

    result = await db.execute(select(User).filter(User.id == user_uuid))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


UPLOAD_DIR = Path('uploads/resumes')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


 # resume_text = extract_text(str(full_file_path))
    # if not resume_text:
    #     raise HTTPException(
    #         status_code=400, detail="Could not extract text from resume")

    # prompt = extract_user_details_from_resume(resume_text)
    # extracted_details = extract_resume_details(prompt)
    # extracted_details = {
    #     "name": "MOHAN TEJA DHARMAVARAPU",
    #     "contact": {
    #         "phone": "+61431097803",
    #         "email": "mohantejad15@gmail.com",
    #         "linkedin": "https://www.linkedin.com/in/mohantejad",
    #         "github": "https://github.com/mohantejad",
    #         "portfolio": "https://mohantejad.vercel.app/"
    #     },
    #     "summary": "Detail-oriented Machine Learning expert with experience over analysing complex datasets to identify trends and support decision-making in high-stakes environments. Proficient in SQL, Python, and data manipulation tools such as Pandas, NumPy, etc. Skilled in developing and maintaining dynamic dashboards and reports for internal and external stakeholders. Adept at collaborating with cross-functional teams, ensuring data accuracy, and delivering actionable insights to optimize performance and mitigate risks. Familiarity with cloud technologies (AWS, GCP) and a proven ability to adapt to fast-paced, dynamic settings.",
    #     "skills": [
    #         "Programming and Scripting: Python and JavaScript",
    #         "Machine Learning: PyTorch, Hugging Face, Generative AI, LLMs",
    #         "Backend: Algorithms & Data Structures, FastAPI, Django",
    #         "Cloud: AWS (EC2, Lambda, Sage Maker, etc), GCP"
    #     ],
    #     "projects": [
    #         {
    #             "name": "Pedestrian Detection",
    #             "description": "Developed real-time computer vision model to detect and track pedestrians on the street. Fine-tuned YOLOv7 model for accuracy and speed, integrated DeepSORT for object tracking.",
    #             "github": "GITHUB"
    #         },
    #         {
    #             "name": "Medical Transcripts Summarization",
    #             "description": "Created an AI model to summarize medical reports, aiding doctors in diagnosing patients. Fine-tuned BERT, GPT, BART, and T5 models, with T5 performing best for summarization tasks.",
    #             "github": "GITHUB"
    #         }
    #     ],
    #     "experience": [
    #         {
    #             "title": "Software Engineer",
    #             "company": "Open Law",
    #             "location": "Sydney, Australia",
    #             "dates": "October 2023 – April 2024",
    #             "description": "Automated data pipelines and data cleaning processes, significantly improving data accessibility and quality for future training and testing. Created and implemented machine learning models using TensorFlow to automate critical tasks, enhancing efficiency and integrated to backend application."
    #         },
    #         {
    #             "title": "Data Analyst Intern",
    #             "company": "University of New South Wales (UNSW)",
    #             "location": "Sydney, Australia",
    #             "dates": "February 2023 – May 2023",
    #             "description": "Conducted in-depth data analysis using Pandas, NumPy, Matplotlib, and Seaborn, providing actionable insights to guide business decisions. A Developed and deployed machine learning models with TensorFlow, automating key processes and improving data handling."
    #         },
    #         {
    #             "title": "Programming Analyst",
    #             "company": "Cognizant Technological Solutions",
    #             "location": "Bangalore, India",
    #             "dates": "January 2019 – December 2019",
    #             "description": "Developed a full-stack application using React.js and Django to display real-time zero-day exploits for the cybersecurity team, automating the tracking and reporting of vulnerabilities. Collaborated with the cybersecurity team to write Python scripts that automated vulnerability assessments using BurpSuite, Wireshark and Metasploit with reporting detailed findings."
    #         }
    #     ],
    #     "education": [
    #         {
    #             "degree": "Master of Information Technology",
    #             "university": "University of New South Wales (UNSW)",
    #             "location": "Sydney, Australia",
    #             "dates": "February 2020 – December 2022"
    #         },
    #         {
    #             "degree": "Bachelor of Computer Science and Engineering",
    #             "university": "Gandhi Institution of Technology and Management (GITAM)",
    #             "location": "Vizag, India",
    #             "dates": "June 2015 – April 2019"
    #         }
    #     ],
    #     "certifications": [
    #         "Data Science, ML and DL Bootcamp Udemy Course – Krish Naik",
    #         "Django and React E-commerce Udemy Course – Dennis Ivy"
    #     ],
    #     "visa": [
    #         "Temporary Graduate Visa",
    #         "Subclass 485 with full work rights in Australia that is valid until May 5, 2028"
    #     ]
    # }

@auth_router.post("/upload-resume")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"uploads/resumes/{file_name}"

    # Save file to disk
    full_file_path = UPLOAD_DIR / file_name
    with full_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.resume_file:
        user.resume_file = ResumeFile(user_id=user.id, file_path=file_path)
    else:
        user.resume_file.file_path = file_path

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Resume uploaded and details updated successfully", 
        'resume_url': user.resume_file
    }


@auth_router.put('/user/update', response_model=UserProfileUpdate)
async def update_user_profile(
    request: Request,
    update_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    try:
        user_uuid = uuid.UUID(user_id)  # Ensure UUID format
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid user ID format')

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    update_dict = update_data.model_dump(exclude_unset=True)
    for field in ['first_name', 'last_name', 'email']:
        if field in update_dict:
            setattr(user, field, update_dict[field])

    if "contact_details" in update_dict:
        if not user.contact_details:
            user.contact_details = ContactDetails(
                **update_dict["contact_details"])
        else:
            for key, value in update_dict["contact_details"].items():
                setattr(user.contact_details, key, value)

    if "experiences" in update_dict:
        user.experiences = [Experience(**exp)
                            for exp in update_dict["experiences"]]

    if "education" in update_dict:
        user.education = [Education(**edu) for edu in update_dict["education"]]

    if "skills" in update_dict:
        user.skills = [UserSkill(**skill) for skill in update_dict["skills"]]

    if "certifications" in update_dict:
        user.certifications = [Certification(
            **cert) for cert in update_dict["certifications"]]

    if "references" in update_dict:
        user.references = [Reference(**ref)
                           for ref in update_dict["references"]]

    if "projects" in update_dict:
        user.projects = [Project(**proj) for proj in update_dict["projects"]]

    if "resume_file" in update_dict:
        if not user.resume_file:
            user.resume_file = ResumeFile(**update_dict["resume_file"])
        else:
            for key, value in update_dict["resume_file"].items():
                setattr(user.resume_file, key, value)

    await db.commit()
    await db.refresh(user)

    return user


# @auth_router.get('/linkedin')
# async def linkedin_login(request: Request):
#     redirect_uri = request.url_for('linkedin_callback')
#     # return redirect_uri._url
#     return await linkedin.authorize_redirect(request, redirect_uri._url)

# @auth_router.get('/linkedin/callback')
# async def linkedin_callback(request: Request, db: AsyncSession = Depends(get_db), response: Response = Response()):
#     token = await linkedin.authorize_access_token(request)
#     async with linkedin.session(token=token['access_token']) as session:
#         user_info = await session.get("https://api.linkedin.com/v2/me")
#         user_email = await session.get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))")
#         user_data = await user_info.json()
#         email_data = await user_email.json()
#         email = email_data["elements"][0]["handle~"]["emailAddress"]

#     if not email:
#         raise HTTPException(status_code=400, detail="OAuth failed")

#     result = await db.execute(select(User).filter(User.email == email))
#     user = result.scalars().first()

#     if not user:
#         user = User(email=email, password_hash="")
#         db.add(user)
#         await db.commit()

#     session_token = generate_session_token()
#     await redis_client.setex(f"session:{session_token}", 86400, str(user.id))

#     response = RedirectResponse(url="/dashboard")
#     response.set_cookie(
#         key="session_token",
#         value=session_token,
#         httponly=True,
#         secure=True,
#         samesite="Lax"
#     )
#     return response
