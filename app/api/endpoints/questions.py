from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.api.dependencies import AsyncSessionDep
from app.models.models import Question
from app.schemas.schemas import Question as QuestionSchema, QuestionCreate, QuestionWithAnswers
from app.utils.logger import logger

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionSchema])
async def get_questions(db: AsyncSessionDep):
    """Получить список всех вопросов"""
    result = await db.execute(select(Question))
    questions = result.scalars().all()
    logger.info(f"Получено {len(questions)} вопросов")
    return questions


@router.post("/", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate, db: AsyncSessionDep):
    """Создать новый вопрос"""
    db_question = Question(text=question.text)
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    logger.info(f"Создан вопрос с id={db_question.id}")
    return db_question


@router.get("/{question_id}", response_model=QuestionWithAnswers)
async def get_question(question_id: int, db: AsyncSessionDep):
    """Получить вопрос и все ответы на него"""
    result = await db.execute(
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.answers))
    )
    question = result.scalar_one_or_none()

    if not question:
        logger.warning(f"Вопрос с id={question_id} не найден")
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, db: AsyncSessionDep):
    """Удалить вопрос вместе с ответами"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        logger.warning(f"Вопрос с id={question_id} не найден")
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    await db.delete(question)
    await db.commit()
    logger.info(f"Удален вопрос с id={question_id}")
    return None