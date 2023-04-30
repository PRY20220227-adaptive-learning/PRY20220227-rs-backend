from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class Teachers(Base):
    __tablename__ = 'Teachers'

    user_id = Column(Integer, ForeignKey('Users.user_id'), primary_key=True)

    user = relationship('Users', back_populates='teacher', uselist=False)
