from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class Question(Base, BaseModel):
    __tablename__ = "questions"

    text = Column(Text, nullable=False)
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base, BaseModel):
    __tablename__ = "answers"

    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=False)
    text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="answers")