import re
from uuid import uuid4
from typing import List, Optional
from annotated_types import MaxLen, MinLen
from typing_extensions import Annotated
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, HttpUrl, UUID4, PastDate


def default_uuid():
    return uuid4()


# ------------------------ CONTACT DETAILS ------------------------


class ContactDetailsBase(BaseModel):
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    github: Optional[HttpUrl]
    portfolio: Optional[HttpUrl]
    linkedin: Optional[HttpUrl]
    location: Optional[str]


class ContactDetailsCreate(ContactDetailsBase):
    email: Annotated[EmailStr, MaxLen(100)]



class ContactDetailsResponse(ContactDetailsBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = {'from_attributes': True}


# ------------------------ EXPERIENCE ------------------------


class ExperienceBase(BaseModel):
    job_title: str
    company: str
    start_date: Annotated[date, PastDate()]
    on_going: Optional[bool] = False
    end_date: Optional[date] = None
    description: Optional[str] = None

    @field_validator('end_date')
    @classmethod
    def check_dates(cls, end_date: Optional[date], values) -> Optional[date]:
        start_date = values.get('start_date')
        on_going = values.get('on_going', False)

        if not on_going and end_date is None:
            raise ValueError("End date is required if the job is not ongoing.")
        if end_date and start_date and end_date < start_date:
            raise ValueError("End date cannot be before start date.")
        return end_date


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ EDUCATION ------------------------


class EducationBase(BaseModel):
    degree: str
    university: str
    graduation_year: Annotated[int, Field(ge=1900, le=datetime.now().year + 10)]



class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ SKILLS ------------------------


class SkillBase(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(50)]


class SkillResponse(SkillBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ CERTIFICATIONS ------------------------


class CertificationBase(BaseModel):
    certification_name: str
    issuer: str
    date_issued: Optional[date] 
    date_expires: Optional[date]


class CertificationCreate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ REFERENCES ------------------------


class ReferenceBase(BaseModel):
    reference_name: str
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: Annotated[EmailStr, MaxLen(100)]

    linkedin: Optional[HttpUrl]
    relation: str


class ReferenceCreate(ReferenceBase):
    pass


class ReferenceResponse(ReferenceBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ PROJECTS ------------------------


class ProjectBase(BaseModel):
    project_name: Annotated[str, MinLen(3), MaxLen(200)]
    description: Optional[str]
    project_link: Optional[HttpUrl]
    demo_link: Optional[HttpUrl]


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID4 = Field(default_factory=default_uuid)

    model_config = ConfigDict(from_attributes=True)


# ------------------------ RESUME FILE ------------------------


class ResumeFileBase(BaseModel):
    file_path: str
    uploaded_at: Optional[datetime]


class ResumeFileResponse(ResumeFileBase):
    id: UUID4 = Field(default_factory=default_uuid)
    user_id: UUID4 

    model_config = ConfigDict(from_attributes=True)

class ResumeFileUpdate(BaseModel):
    file_path: str
    upload_date: Optional[datetime] = None


# ------------------------ USER SCHEMAS ------------------------


class UserBase(BaseModel):
    first_name: Annotated[str, MinLen(2), MaxLen(100)]
    last_name: Annotated[str, MinLen(2), MaxLen(100)]
    email: Annotated[EmailStr, MaxLen(100)]


class UserCreateBase(BaseModel):
    email: Annotated[EmailStr, MaxLen(100)]

    password: Annotated[str, MinLen(6), MaxLen(100)]

class UserCreate(UserBase):
    password: Annotated[str, MinLen(6), MaxLen(100)]

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one number.")
        return password


class UserResponse(UserBase):
    id: UUID4 = Field(default_factory=default_uuid)
    create_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ------------------------ FULL USER PROFILE ------------------------


class UserProfileResponse(UserResponse):
    contact_details: Optional[ContactDetailsResponse]
    experiences: List[ExperienceResponse]
    education: List[EducationResponse]
    skills: List[SkillResponse]
    certifications: List[CertificationResponse]
    references: List[ReferenceResponse]
    projects: List[ProjectResponse]
    resume_file: Optional[ResumeFileResponse]

class UserProfileUpdate(BaseModel):
    first_name: Optional[Annotated[str, MinLen(2), MaxLen(100)]] = None
    last_name: Optional[Annotated[str, MinLen(2), MaxLen(100)]] = None
    contact_details: Optional[ContactDetailsCreate] = None
    experiences: Optional[List[ExperienceCreate]] = None
    education: Optional[List[EducationCreate]] = None
    skills: Optional[List[SkillBase]] = None
    certifications: Optional[List[CertificationCreate]] = None
    references: Optional[List[ReferenceCreate]] = None
    projects: Optional[List[ProjectCreate]] = None
    resume_file: Optional[ResumeFileBase] = None

    model_config = ConfigDict(from_attributes=True)
