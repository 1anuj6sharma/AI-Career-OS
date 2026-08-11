from sqlalchemy import Column, Integer, String, Text, Float, Date, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    
    # Basic
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    phone = Column(String(20))
    location = Column(String(200))
    bio = Column(Text)
    
    # Professional
    professional_headline = Column(String(300))
    current_role = Column(String(200))
    target_role = Column(String(200))
    years_of_experience = Column(Float)
    preferred_job_type = Column(String(50))  # full-time, part-time, contract, internship
    preferred_location = Column(String(200))
    work_preference = Column(String(50))  # remote, hybrid, onsite
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship('User', back_populates='profile')


class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # technical, soft, language, framework, database, tool
    proficiency_level = Column(String(20))  # beginner, intermediate, advanced, expert
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship('User', backref='skills')


class Education(Base):
    __tablename__ = 'education'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    degree = Column(String(200), nullable=False)
    institution = Column(String(300), nullable=False)
    field_of_study = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    gpa = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship('User', backref='education_records')


class Experience(Base):
    __tablename__ = 'experience'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    role = Column(String(200), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)  # null = current
    description = Column(Text)
    technologies = Column(JSON)  # List of strings
    achievements = Column(JSON)  # List of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship('User', backref='experiences')


class Certification(Base):
    __tablename__ = 'certifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(300), nullable=False)
    issuer = Column(String(300), nullable=False)
    issue_date = Column(Date)
    expiry_date = Column(Date)
    credential_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship('User', backref='certifications')


class CareerPreference(Base):
    __tablename__ = 'career_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    target_roles = Column(JSON)  # List of strings
    target_companies = Column(JSON)  # List of strings
    target_salary_min = Column(Integer)
    target_salary_max = Column(Integer)
    preferred_locations = Column(JSON)  # List of strings
    career_objectives = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship('User', backref='career_preference')
