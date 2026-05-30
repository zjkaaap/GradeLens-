from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship(
        "Question",
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), index=True)
    qno = Column(String(16))
    stem = Column(Text)
    answer = Column(Text)
    explanation = Column(Text)
    score = Column(Integer, default=5)

    paper = relationship("Paper", back_populates="questions")


class GradingRecord(Base):
    __tablename__ = "grading_records"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, index=True)
    question_id = Column(Integer)
    image_path = Column(String(512))
    student_ocr = Column(Text)
    score_obtained = Column(Integer)
    full_score = Column(Integer)
    deduction_reason = Column(Text)
    ai_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
