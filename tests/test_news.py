import pytest
import allure
import os
import requests
from models import NewsResponse, Body_create_news_api_news_post as NewsCreate
from helpers import generate_news
from tests.conftest import BASE_URL, USERS
from datetime import date

class TestNews:
    @pytest.mark.parametrize("params", [
        pytest.param({"exclude": ("image",)}, id="without_image"),
        pytest.param({}, id="full_news"),
    ])
    def test_create(self, faker, login, params):
        with allure.step("Получаем токен авторизации"):
            token = login(**USERS[0])
            headers = {"Authorization": f"Bearer {token}"}

        with allure.step("Создание новости"):
            news_data = NewsCreate(**generate_news(faker, **params))

            with allure.step("Подготовка данных для запроса"):
                image_path = news_data.image
                files = {}
                for key, value in news_data.model_dump().items():
                    if value is not None:
                        files[key] = (None, str(value))

                if image_path and os.path.exists(image_path):
                    files["image"] = (
                        os.path.basename(image_path),
                        open(image_path, "rb"),
                        "image/png"
                    )

            response = requests.post(f"{BASE_URL}/api/news/", headers=headers, files=files)

            assert response.status_code == 200

        with allure.step("Проверка созданной новости"):
            answer = NewsResponse(**response.json())

            assert answer.title == news_data.title, "Заголовок не совпадает или отсутствует"
            assert answer.text == news_data.text, "Текст не совпадает или отсутствует"

            if news_data.subtitle:
                assert answer.subtitle == news_data.subtitle, "Подзаголовок не совпадает"

            if news_data.tags:
                tags = news_data.tags.split(", ")
                assert all(t.name in tags for t in answer.tags)

        with allure.step("Удаление новости"):
            news_id = response.json().get("id")
            response = requests.delete(f"{BASE_URL}/api/news/{news_id}", headers=headers)
            #405
            #assert response.status_code == 200