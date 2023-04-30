from typing import List
from pydantic import BaseModel, Field
from schemas.user import UserCreate, UserUpdate


class TeacherCreate(UserCreate):
    pass


class TeacherUpdate(UserUpdate):
    pass


class Teacher(TeacherCreate):
    user_id: int
    is_teacher: bool = True

    class Config:
        orm_mode = True


class TeacherBase(BaseModel):
    user_id: int
    name: str
    lastname: str
    username: str
    class_: str
    course: str


class TeachersResponse(BaseModel):
    __root__: List[TeacherBase] = Field(..., alias="")
