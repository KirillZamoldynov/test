from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import List


class AnswerBase(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    user_id: str = Field(min_length=1, max_length=36)

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        # Обрезать пробелы и проверить на пустоту
        v = v.strip()
        if not v:
            raise ValueError('Текст ответа не может быть пустым')
        return v

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        # Обрезать пробелы и проверить на пустоту
        v = v.strip()
        if not v:
            raise ValueError('Идентификатор пользователя не может быть пустым')
        return v


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    question_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    text: str = Field(min_length=1, max_length=1000)

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        # Обрезать пробелы и проверить на пустоту
        v = v.strip()
        if not v:
            raise ValueError('Текст вопроса не может быть пустым')
        return v


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class QuestionWithAnswers(Question):
    answers: List[Answer] = Field(default_factory=list)