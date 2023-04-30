from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from models.user import Users
from models.teacher import Teachers
from models.student import Students

from schemas.student import StudentBase, StudentCreate
from schemas.teacher import TeacherBase, TeacherCreate
from schemas.user import UserLogin, UserLoginResponse

from database.connection import Database


router = APIRouter()
database = Database()


@router.post('/login', response_model=UserLoginResponse)
async def users_login(user_login: UserLogin, db: Session = Depends(database.get_db_session)):
    user = db.query(Users).filter(
        Users.username == user_login.username).first()
    if not user or user.password != user_login.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")

    # check if user_id is in students table
    student = db.query(Students).filter(
        Students.user_id == user.user_id).first()
    if student:
        user_type = "student"
        user_info = student
    else:
        # check if user_id is in teachers table
        teacher = db.query(Teachers).filter(
            Teachers.user_id == user.user_id).first()
        if teacher:
            user_type = "teacher"
            user_info = None  # Set to None if teacher
        else:
            user_type = "unknown"
            user_info = None

    # Define response data
    response_data = {
        "user_id": user.user_id,
        "name": user.name,
        "lastname": user.lastname,
        "username": user.username,
        "class_": user.class_,
        "course": user.course
    }

    # Add optional fields based on user type
    if user_type == "student":
        response_data["knowledge_level"] = user_info.knowledge_level
        response_data["mark"] = user_info.mark
        response_data["learning_style"] = user_info.learning_style

    return response_data


@router.get('')
async def get_users(db: Session = Depends(database.get_db_session)):
    return db.query(Users).all()


@router.get('/{id}')
async def get_user_by_id(id: int, db: Session = Depends(database.get_db_session)):
    user = db.query(Users).filter(Users.user_id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post('/students')
async def create_student(student: StudentCreate, db: Session = Depends(database.get_db_session)):
    user = Users(
        name=student.name,
        lastname=student.lastname,
        username=student.username,
        password=student.password,
        class_=student.class_,
        course=student.course
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db_student_data = {
        k: v for k, v in student.dict().items()
        if k in {'knowledge_level', 'mark', 'learning_style'}
    }
    db_student = Students(user_id=user.user_id, **db_student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get('/students/registered')
async def get_students(db: Session = Depends(database.get_db_session)):
    students = db.query(Students, Users).join(
        Users, Students.user_id == Users.user_id).all()

    student_list = []
    for student, user in students:
        student_data = StudentBase(
            user_id=student.user_id,
            name=user.name,
            lastname=user.lastname,
            username=user.username,
            class_=user.class_,
            course=user.course,
            knowledge_level=student.knowledge_level,
            mark=student.mark,
            learning_style=student.learning_style,
        )
        student_list.append(student_data)

    return student_list


@router.post("/teachers")
async def create_teacher(teacher: TeacherCreate, db: Session = Depends(database.get_db_session)):
    user = Users(
        name=teacher.name,
        lastname=teacher.lastname,
        username=teacher.username,
        password=teacher.password,
        class_=teacher.class_,
        course=teacher.course
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db_teacher = Teachers(user_id=user.user_id)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.get('/teachers/registered')
async def get_teachers(db: Session = Depends(database.get_db_session)):
    teachers = db.query(Teachers, Users).join(
        Users, Teachers.user_id == Users.user_id).all()

    teacher_list = []
    for teacher, user in teachers:
        teacher_data = TeacherBase(
            user_id=teacher.user_id,
            name=user.name,
            lastname=user.lastname,
            username=user.username,
            class_=user.class_,
            course=user.course,
        )
        teacher_list.append(teacher_data)

    return teacher_list


@router.get("/students/{class_code}", response_model=List[StudentBase])
async def get_students_by_class(class_code: str, db: Session = Depends(database.get_db_session)):
    users = db.query(Users).filter_by(class_=class_code).all()
    if not users:
        raise HTTPException(
            status_code=404, detail="No existen estudiantes para esta clase")

    students = []
    for user in users:
        if user.student:
            student = user.student
            student_dict = student.__dict__
            student_dict.update(user.__dict__)
            student_dict.pop('_sa_instance_state', None)
            student_dict.pop('password', None)
            students.append(student_dict)

    return students
