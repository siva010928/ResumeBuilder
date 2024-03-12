from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl, constr, validator

from app.utils.helpers import trim_mobile_no


class ProfileSchema(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    location: constr(strip_whitespace=True, min_length=1)
    phone: constr(min_length=1)
    email: EmailStr
    linkedin_username: constr(strip_whitespace=True, min_length=1)

    _validate_phone = validator('phone', allow_reuse=True, pre=True)(trim_mobile_no)


class EducationSchema(BaseModel):
    institution: constr(strip_whitespace=True, min_length=1)
    location: constr(strip_whitespace=True, min_length=1)
    degree: Optional[constr(strip_whitespace=True, min_length=1)] = None
    duration: constr(strip_whitespace=True, min_length=1)

    class Config:
        orm_mode = True


class ExperienceSchema(BaseModel):
    role: constr(strip_whitespace=True, min_length=1)
    company: constr(strip_whitespace=True, min_length=1)
    location: Optional[constr(strip_whitespace=True, min_length=1)] = None
    duration: constr(strip_whitespace=True, min_length=1)
    description: List[constr(strip_whitespace=True, min_length=1)] = []

    class Config:
        orm_mode = True


class ProjectSchema(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    duration: constr(strip_whitespace=True, min_length=1)
    description: List[constr(strip_whitespace=True, min_length=1)] = []

    class Config:
        orm_mode = True


class AchievementSchema(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    description: List[constr(strip_whitespace=True, min_length=1)] = []

    class Config:
        orm_mode = True


class SkillSchema(BaseModel):
    skill: constr(strip_whitespace=True, min_length=1)
    value: constr(strip_whitespace=True, min_length=1)

    class Config:
        orm_mode = True


class ProfileLinkSchema(BaseModel):
    platform: constr(strip_whitespace=True, min_length=1)
    url: str

    class Config:
        orm_mode = True


class ResumeSchema(BaseModel):
    profile: ProfileSchema
    education: List[EducationSchema]
    experience: List[ExperienceSchema]
    project: List[ProjectSchema]
    skill: List[SkillSchema]
    achievement: List[AchievementSchema]
    profile_links: List[ProfileLinkSchema]
