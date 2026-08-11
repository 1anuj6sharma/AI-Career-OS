from sqlalchemy.orm import Session
from typing import Optional, List, Type
from app.modules.profile.models import Profile, Skill, Education, Experience, Certification, CareerPreference

class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()
    
    def create(self, profile: Profile) -> Profile:
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile
    
    def update(self, profile: Profile) -> Profile:
        self.db.flush()
        self.db.refresh(profile)
        return profile


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[Skill]:
        return self.db.query(Skill).filter(Skill.user_id == user_id).all()

    def get_by_id_and_user(self, skill_id: int, user_id: int) -> Optional[Skill]:
        return self.db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == user_id).first()

    def create(self, skill: Skill) -> Skill:
        self.db.add(skill)
        self.db.flush()
        self.db.refresh(skill)
        return skill

    def update(self, skill: Skill) -> Skill:
        self.db.flush()
        self.db.refresh(skill)
        return skill

    def delete(self, skill: Skill) -> None:
        self.db.delete(skill)
        self.db.flush()


class EducationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[Education]:
        return self.db.query(Education).filter(Education.user_id == user_id).all()

    def get_by_id_and_user(self, education_id: int, user_id: int) -> Optional[Education]:
        return self.db.query(Education).filter(Education.id == education_id, Education.user_id == user_id).first()

    def create(self, education: Education) -> Education:
        self.db.add(education)
        self.db.flush()
        self.db.refresh(education)
        return education

    def update(self, education: Education) -> Education:
        self.db.flush()
        self.db.refresh(education)
        return education

    def delete(self, education: Education) -> None:
        self.db.delete(education)
        self.db.flush()


class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[Experience]:
        return self.db.query(Experience).filter(Experience.user_id == user_id).all()
        
    def get_by_id_and_user(self, experience_id: int, user_id: int) -> Optional[Experience]:
        return self.db.query(Experience).filter(Experience.id == experience_id, Experience.user_id == user_id).first()

    def create(self, experience: Experience) -> Experience:
        self.db.add(experience)
        self.db.flush()
        self.db.refresh(experience)
        return experience

    def update(self, experience: Experience) -> Experience:
        self.db.flush()
        self.db.refresh(experience)
        return experience

    def delete(self, experience: Experience) -> None:
        self.db.delete(experience)
        self.db.flush()


class CertificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[Certification]:
        return self.db.query(Certification).filter(Certification.user_id == user_id).all()

    def get_by_id_and_user(self, certification_id: int, user_id: int) -> Optional[Certification]:
        return self.db.query(Certification).filter(Certification.id == certification_id, Certification.user_id == user_id).first()

    def create(self, certification: Certification) -> Certification:
        self.db.add(certification)
        self.db.flush()
        self.db.refresh(certification)
        return certification

    def update(self, certification: Certification) -> Certification:
        self.db.flush()
        self.db.refresh(certification)
        return certification

    def delete(self, certification: Certification) -> None:
        self.db.delete(certification)
        self.db.flush()


class CareerPreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[CareerPreference]:
        return self.db.query(CareerPreference).filter(CareerPreference.user_id == user_id).first()
        
    def create(self, preference: CareerPreference) -> CareerPreference:
        self.db.add(preference)
        self.db.flush()
        self.db.refresh(preference)
        return preference
        
    def update(self, preference: CareerPreference) -> CareerPreference:
        self.db.flush()
        self.db.refresh(preference)
        return preference
