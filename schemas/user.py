from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str
    lastname: str
    username: str
    password: str
    class_: str
    course: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    user_id: int


class User(UserBase):
    user_id: Optional[int] = None
    is_student: bool = False
    is_teacher: bool = False

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    user_id: int
    name: str
    lastname: str
    username: str
    class_: str
    course: str

    class Config:
        orm_mode = True


class UserLoginResponse(BaseModel):
    user_id: int
    name: str
    lastname: str
    username: str
    class_: str
    course: str
    knowledge_level: Optional[str] = None
    mark: Optional[float] = None
    learning_style: Optional[str] = None
