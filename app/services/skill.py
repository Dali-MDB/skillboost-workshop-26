from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.skill import SkillRepository, UserSkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate, UserSkillDisplay
from app.models.skill import Skill, UserSkill
from app.models.user import User


class SkillService:
    def __init__(self, db: Session) -> None:
        self.repo = SkillRepository(db)

    def create_skill(self, data: SkillCreate) -> Skill:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill already exists")
        return self.repo.create(name=data.name, category=data.category, description=data.description)

    def list_skills(self) -> List[Skill]:
        return self.repo.list_all()

    def update_skill(self, skill_id: int, data: SkillUpdate) -> Skill:
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
        return self.repo.update(skill, **data.model_dump(exclude_unset=True))

    def delete_skill(self, skill_id: int) -> None:
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
        self.repo.delete(skill)


class UserSkillService:
    def __init__(self, db: Session) -> None:
        self.repo = UserSkillRepository(db)
        self.skill_repo = SkillRepository(db)

    def _to_display(self, us: UserSkill) -> UserSkillDisplay:
        return UserSkillDisplay(
            id=us.id,
            skill_id=us.skill_id,
            skill_name=us.skill.name,
            level=us.level,
        )

    def learn(self, user: User, skill_id: int) -> UserSkillDisplay:
        if not self.skill_repo.get_by_id(skill_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
        if self.repo.get(user.id, skill_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill already learned")
        us = self.repo.create(user_id=user.id, skill_id=skill_id, level=1)
        return self._to_display(us)

    def list_my_skills(self, user: User) -> List[UserSkillDisplay]:
        return [self._to_display(us) for us in self.repo.list_for_user(user.id)]

    def level_up(self, user: User, skill_id: int) -> UserSkillDisplay:
        us = self.repo.get(user.id, skill_id)
        if not us:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You haven't learned this skill")
        us = self.repo.increment_level(us, 1)
        return self._to_display(us)

    def unlearn(self, user: User, skill_id: int) -> None:
        us = self.repo.get(user.id, skill_id)
        if not us:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You haven't learned this skill")
        self.repo.delete(us)
