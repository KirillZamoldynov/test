from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import AsyncSessionDep
from app.models.models import Answer, Question
from app.schemas.schemas import Answer as AnswerSchema, AnswerCreate
from app.utils.logger import logger

router = APIRouter(tags=["answers"])


@router.post("/questions/{question_id}/answers/", response_model=AnswerSchema, status_code=status.HTTP_201_CREATED)
async def create_answer(question_id: int, answer: AnswerCreate, db: AsyncSessionDep):
    """Добавить ответ к вопросу"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        logger.warning(f"Попытка создать ответ для несуществующего вопроса id={question_id}")
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    db_answer = Answer(
        question_id=question_id,
        user_id=answer.user_id,
        text=answer.text
    )
    db.add(db_answer)
    await db.commit()
    await db.refresh(db_answer)
    logger.info(f"Создан ответ с id={db_answer.id} для вопроса id={question_id}")
    return db_answer


@router.get("/answers/{answer_id}", response_model=AnswerSchema)
async def get_answer(answer_id: int, db: AsyncSessionDep):
    """Получить конкретный ответ"""
    result = await db.execute(
        select(Answer).where(Answer.id == answer_id)
    )
    answer = result.scalar_one_or_none()

    if not answer:
        logger.warning(f"Ответ с id={answer_id} не найден")
        raise HTTPException(status_code=404, detail="Ответ не найден")

    return answer


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(answer_id: int, db: AsyncSessionDep):
    """Удалить ответ"""
    result = await db.execute(
        select(Answer).where(Answer.id == answer_id)
    )
    answer = result.scalar_one_or_none()

    if not answer:
        logger.warning(f"Ответ с id={answer_id} не найден")
        raise HTTPException(status_code=404, detail="Ответ не найден")

    await db.delete(answer)
    await db.commit()
    logger.info(f"Удален ответ с id={answer_id}")
    return None