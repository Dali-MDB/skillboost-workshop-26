from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.skill import Skill, UserSkill


class SkillRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def get_by_name(self, name: str) -> Optional[Skill]:
        return self.db.query(Skill).filter(Skill.name == name).first()

    def list_all(self) -> List[Skill]:
        return self.db.query(Skill).all()

    def create(self, name: str, category: str, description: Optional[str]) -> Skill:
        skill = Skill(name=name, category=category, description=description)
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def update(self, skill: Skill, **kwargs) -> Skill:
        for field, value in kwargs.items():
            if value is not None:
                setattr(skill, field, value)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def delete(self, skill: Skill) -> None:
        self.db.delete(skill)
        self.db.commit()


class UserSkillRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int, skill_id: int) -> Optional[UserSkill]:
        return (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> List[UserSkill]:
        return self.db.query(UserSkill).filter(UserSkill.user_id == user_id).all()

    def create(self, user_id: int, skill_id: int, level: int = 1) -> UserSkill:
        user_skill = UserSkill(user_id=user_id, skill_id=skill_id, level=level)
        self.db.add(user_skill)
        self.db.commit()
        self.db.refresh(user_skill)
        return user_skill

    def update_level(self, user_skill: UserSkill, level: int) -> UserSkill:
        user_skill.level = level
        self.db.commit()
        self.db.refresh(user_skill)
        return user_skill

    def increment_level(self, user_skill: UserSkill, amount: int = 1) -> UserSkill:
        user_skill.level = (user_skill.level or 0) + amount
        self.db.commit()
        self.db.refresh(user_skill)
        return user_skill

    def delete(self, user_skill: UserSkill) -> None:
        self.db.delete(user_skill)
        self.db.commit()
