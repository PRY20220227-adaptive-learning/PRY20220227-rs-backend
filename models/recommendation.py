from sqlalchemy import Column, Integer, String, Date, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from database.connection import Base


class Recommendations(Base):
    __tablename__ = 'Recommendations'

    recommendation_id = Column(Integer, Sequence('recommendation_id_seq'),
                               primary_key=True, index=True)
    date = Column(Date, nullable=False)
    url = Column(String(200), nullable=False)
    topic = Column(String(30), nullable=False)
    student_id = Column(Integer, ForeignKey(
        'Students.user_id'), nullable=False)

    student = relationship('Students', back_populates='recommendations')
