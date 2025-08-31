import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_question(client: AsyncClient):
    response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос?"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тестовый вопрос?"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient):
    await client.post("/questions/", json={"text": "Вопрос 1"})
    await client.post("/questions/", json={"text": "Вопрос 2"})

    response = await client.get("/questions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_create_answer(client: AsyncClient):
    question_response = await client.post(
        "/questions/",
        json={"text": "Вопрос для ответа"}
    )
    question_id = question_response.json()["id"]

    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "user123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тестовый ответ"
    assert data["user_id"] == "user123"


@pytest.mark.asyncio
async def test_delete_question_with_answers(client: AsyncClient):
    question_response = await client.post(
        "/questions/",
        json={"text": "Вопрос для удаления"}
    )
    question_id = question_response.json()["id"]

    await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Ответ 1", "user_id": "user1"}
    )

    response = await client.delete(f"/questions/{question_id}")
    assert response.status_code == 204

    response = await client.get(f"/questions/{question_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.asyncio
async def test_create_question_empty_text(client: AsyncClient):
    # Проверка валидации пустого текста вопроса
    response = await client.post(
        "/questions/",
        json={"text": "   "}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_empty_text(client: AsyncClient):
    # Создаем вопрос для теста
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    # Проверка валидации пустого текста ответа
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "   ", "user_id": "user123"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_answer_empty_user_id(client: AsyncClient):
    # Создаем вопрос для теста
    question_response = await client.post(
        "/questions/",
        json={"text": "Тестовый вопрос"}
    )
    question_id = question_response.json()["id"]

    # Проверка валидации пустого user_id
    response = await client.post(
        f"/questions/{question_id}/answers/",
        json={"text": "Тестовый ответ", "user_id": "   "}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_answer(client: AsyncClient):
    # Создаем вопрос и ответ для теста
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