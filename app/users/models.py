from datetime import datetime, date, timezone
from typing import List, Optional
import uuid
import bcrypt
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, Boolean, Column, DateTime, Text, func, ForeignKey, String, CheckConstraint
from app.database import Base


# ------------------------ CONTACT DETAILS ------------------------


class ContactDetails(Base):
    __tablename__ = "contact_details"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), CheckConstraint(
        "phone ~ '^\\+?[1-9][0-9]{6,14}$'", name="valid_phone"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), CheckConstraint(
        "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="valid_email"), nullable=False)
    github: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="contact_details")


# ------------------------ EXPERIENCE ------------------------


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    on_going: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="experiences")

    __table_args__ = (
        CheckConstraint("on_going OR end_date IS NOT NULL",
                        name="check_experience_end_date"),
    )


# ------------------------ EDUCATION ------------------------


class Education(Base):
    __tablename__ = "education"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    graduation_year: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="education")


# ------------------------ SKILLS ------------------------


class SkillMaster(Base):
    __tablename__ = "skill_master"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class UserSkill(Base):
    __tablename__ = "user_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "skill_master.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="skills")
    skill: Mapped["SkillMaster"] = relationship()


# ------------------------ CERTIFICATIONS ------------------------


class Certification(Base):
    __tablename__ = 'certifications'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    certification_name: Mapped[str] = mapped_column(
        String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=True)
    date_issued: Mapped[date] = mapped_column(nullable=True)
    date_expires: Mapped[Optional[date]] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="certifications")


# ------------------------ REFERENCES ------------------------


class Reference(Base):
    __tablename__ = "references"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), CheckConstraint(
        "phone ~ '^\\+?[1-9][0-9]{6,14}$'", name="valid_phone"))
    email: Mapped[str] = mapped_column(String(255), CheckConstraint(
        "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="valid_email"), unique=True, nullable=False)
    linkedin: Mapped[Optional[str]] = mapped_column(String(255))
    relation: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship(back_populates="references")


# ------------------------ PROJECTS ------------------------


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_link: Mapped[Optional[str]] = mapped_column(String(255))
    demo_link: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="projects")


# ------------------------ RESUME FILE ------------------------


class ResumeFile(Base):
    __tablename__ = "resume_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None))

    user: Mapped["User"] = relationship(back_populates="resume_file")


# ------------------------ BASE USER ------------------------


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), CheckConstraint(
        "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="valid_email"), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    create_date = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None))
    update_date = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None), onupdate=lambda: datetime.now().replace(tzinfo=None))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    contact_details: Mapped[Optional[ContactDetails]] = relationship(
        back_populates="user", lazy="joined")
    experiences: Mapped[List[Experience]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    education: Mapped[List[Education]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    skills: Mapped[List[UserSkill]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    certifications: Mapped[List[Certification]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    references: Mapped[List[Reference]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    projects: Mapped[List[Project]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    resume_file: Mapped[Optional[ResumeFile]] = relationship(
        back_populates="user", cascade="save-update, merge", lazy="joined", uselist=False
    )

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

    def verify_password(self, plain_password: str) -> bool:
        """Verify password using bcrypt"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password_hash.encode('utf-8'))
