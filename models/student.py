from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.recommendation import Recommendations
from database.connection import Base


class Students(Base):
    __tablename__ = 'Students'

    user_id = Column(Integer, ForeignKey('Users.user_id'), primary_key=True)
    knowledge_level = Column(String(20), nullable=False)
    mark = Column(Float(precision=2), nullable=False)
    learning_style = Column(String(20), nullable=False)

    user = relationship('Users', back_populates='student', uselist=False)
    recommendations = relationship('Recommendations', back_populates='student')
