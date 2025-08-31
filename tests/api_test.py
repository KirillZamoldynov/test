import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Тест проверки состояния сервиса"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "healthy"
    assert data["database"] == "healthy"


@pytest.mark.asyncio
async def test_create_question(client: AsyncClient):
    """Тест создания вопроса"""
    response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос?"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тестовый вопрос?"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient):
    """Тест получения списка вопросов"""
    # Создаем тестовые вопросы
    await client.post("/questions/", json={"text": "Вопрос 1"})
    await client.post("/questions/", json={"text": "Вопрос 2"})

    # Получаем список
    response = await client.get("/questions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert all("id" in question for question in data)


@pytest.mark.asyncio
async def test_get_question_by_id(client: AsyncClient):
    """Тест получения конкретного вопроса с ответами"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Вопрос для получения"}
    )
    question_id = question_response.json()["id"]

    # Добавляем ответ
    await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "user123"}
    )

    # Получаем вопрос с ответами
    response = await client.get(f"/questions/{question_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Вопрос для получения"
    assert "answers" in data
    assert len(data["answers"]) == 1


@pytest.mark.asyncio
async def test_create_answer(client: AsyncClient):
    """Тест создания ответа на вопрос"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Вопрос для ответа"}
    )
    question_id = question_response.json()["id"]

    # Создаем ответ
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "user123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тестовый ответ"
    assert data["user_id"] == "user123"
    assert data["question_id"] == question_id
    assert "id" in data


@pytest.mark.asyncio
async def test_get_answer_by_id(client: AsyncClient):
    """Тест получения конкретного ответа"""
    # Создаем вопрос и ответ
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    answer_response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "user123"}
    )
    answer_id = answer_response.json()["id"]

    # Получаем ответ
    response = await client.get(f"/answers/{answer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Тестовый ответ"
    assert data["user_id"] == "user123"


@pytest.mark.asyncio
async def test_delete_answer(client: AsyncClient):
    """Тест удаления ответа"""
    # Создаем вопрос и ответ
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    answer_response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "user123"}
    )
    answer_id = answer_response.json()["id"]

    # Удаляем ответ
    response = await client.delete(f"/answers/{answer_id}")
    assert response.status_code == 204

    # Проверяем что ответ удален
    response = await client.get(f"/answers/{answer_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_question_with_cascade(client: AsyncClient):
    """Тест CASCADE удаления вопроса вместе с ответами"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Вопрос для удаления"}
    )
    question_id = question_response.json()["id"]

    # Добавляем несколько ответов
    answer1_response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Ответ 1", "user_id": "user1"}
    )
    answer2_response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Ответ 2", "user_id": "user2"}
    )

    answer1_id = answer1_response.json()["id"]
    answer2_id = answer2_response.json()["id"]

    # Удаляем вопрос
    response = await client.delete(f"/questions/{question_id}")
    assert response.status_code == 204

    # Проверяем что вопрос удален
    response = await client.get(f"/questions/{question_id}")
    assert response.status_code == 404

    # Проверяем что ответы тоже удалены (CASCADE)
    response = await client.get(f"/answers/{answer1_id}")
    assert response.status_code == 404
    response = await client.get(f"/answers/{answer2_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_question_validation_empty_text(client: AsyncClient):
    """Тест валидации пустого текста вопроса"""
    response = await client.post(
        "/questions/",
        json={"text": "   "}
    )
    assert response.status_code == 422
    error = response.json()
    assert "detail" in error


@pytest.mark.asyncio
async def test_create_question_validation_long_text(client: AsyncClient):
    """Тест валидации слишком длинного текста вопроса"""
    long_text = "А" * 1001  # Превышаем лимит в 1000 символов
    response = await client.post(
        "/questions/",
        json={"text": long_text}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_validation_empty_text(client: AsyncClient):
    """Тест валидации пустого текста ответа"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    # Попытка создать ответ с пустым текстом
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "   ", "user_id": "user123"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_validation_empty_user_id(client: AsyncClient):
    """Тест валидации пустого user_id"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    # Попытка создать ответ с пустым user_id
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "   "}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_validation_long_text(client: AsyncClient):
    """Тест валидации слишком длинного текста ответа"""
    # Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    # Попытка создать ответ со слишком длинным текстом
    long_text = "Б" * 501  # Превышаем лимит в 500 символов
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": long_text, "user_id": "user123"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_nonexistent_question(client: AsyncClient):
    """Тест создания ответа на несуществующий вопрос"""
    response = await client.post(
        "/questions/999999/answers/",
        json={"text": "Ответ на несуществующий вопрос", "user_id": "user123"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_question(client: AsyncClient):
    """Тест получения несуществующего вопроса"""
    response = await client.get("/questions/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_answer(client: AsyncClient):
    """Тест получения несуществующего ответа"""
    response = await client.get("/answers/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_question(client: AsyncClient):
    """Тест удаления несуществующего вопроса"""
    response = await client.delete("/questions/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_answer(client: AsyncClient):
    """Тест удаления несуществующего ответа"""
    response = await client.delete("/answers/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_complete_workflow(client: AsyncClient):
    """Интеграционный тест полного рабочего процесса"""
    # 1. Создаем вопрос
    question_response = await client.post(
        "/questions/",
        json={"text": "Сколько будет 2+2?"}
    )
    assert question_response.status_code == 201
    question_id = question_response.json()["id"]

    # 2. Получаем список вопросов
    questions_response = await client.get("/questions/")
    assert questions_response.status_code == 200
    questions = questions_response.json()
    assert any(q["id"] == question_id for q in questions)

    # 3. Добавляем ответы
    answers_data = [
        {"text": "4", "user_id": "ученик1"},
        {"text": "Четыре", "user_id": "ученик2"},
        {"text": "2+2=4", "user_id": "ученик3"}
    ]

    answer_ids = []
    for answer_data in answers_data:
        response = await client.post(
            f"/questions/{question_id}/answers/",
            json=answer_data
        )
        assert response.status_code == 201
        answer_ids.append(response.json()["id"])

    # 4. Получаем вопрос с ответами
    question_with_answers = await client.get(f"/questions/{question_id}")
    assert question_with_answers.status_code == 200
    data = question_with_answers.json()
    assert len(data["answers"]) == 3

    # 5. Удаляем один ответ
    delete_response = await client.delete(f"/answers/{answer_ids[0]}")
    assert delete_response.status_code == 204

    # 6. Проверяем что ответ удалился
    updated_question = await client.get(f"/questions/{question_id}")
    assert len(updated_question.json()["answers"]) == 2

    # 7. Удаляем вопрос (CASCADE удалит оставшиеся ответы)
    delete_question_response = await client.delete(f"/questions/{question_id}")
    assert delete_question_response.status_code == 204

    # 8. Проверяем что всё удалилось
    assert (await client.get(f"/questions/{question_id}")).status_code == 404
    for answer_id in answer_ids[1:]:  # Первый уже удален ранее
        assert (await client.get(f"/answers/{answer_id}")).status_code == 404