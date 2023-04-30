from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from database.connection import Base


class Users(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, Sequence('user_id_seq'),
                     primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(20), nullable=False)
    class_ = Column('class', String(10), nullable=False)
    course = Column(String(40), nullable=False)

    student = relationship('Students', back_populates='user', uselist=False)
    teacher = relationship('Teachers', back_populates='user', uselist=False)
