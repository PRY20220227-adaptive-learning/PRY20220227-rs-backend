from typing import List
from models.student import Students
from typing import Optional
from pydantic import BaseModel, Field

from schemas.user import UserCreate, UserRead, UserUpdate


class StudentCreate(UserCreate):
    knowledge_level: str
    mark: float
    learning_style: str


class StudentUpdate(UserUpdate):
    knowledge_level: Optional[str]
    mark: Optional[float]
    learning_style: Optional[str]


class Student(StudentCreate):
    user_id: int
    is_student: bool = True

    class Config:
        orm_mode = True


class StudentRead(BaseModel):
    user: UserRead
    knowledge_level: str
    mark: float
    learning_style: str

    class Config:
        orm_mode = True


class StudentsResponse(BaseModel):
    students: List[Students]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StudentOut(BaseModel):
    user_id: int
    knowledge_level: str
    mark: float
    learning_style: str

    class Config:
        orm_mode = True


class StudentBase(BaseModel):
    user_id: int
    name: str
    lastname: str
    username: str
    class_: str
    course: str
    knowledge_level: str
    mark: float
    learning_style: str


class StudentsResponse(BaseModel):
    __root__: List[StudentBase] = Field(..., alias="")
