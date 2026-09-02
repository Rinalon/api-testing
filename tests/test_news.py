import pytest
import allure
import os
import requests
from models import NewsResponse, Body_create_news_api_news_post as NewsCreate
from helpers import generate_news
from tests.conftest import BASE_URL, USERS, create_news, make_files
from datetime import date

class TestNews:
    news_url = BASE_URL + "/api/news/"

    @allure.story("Проверка создания новости")
    @pytest.mark.parametrize("params", [
        pytest.param({"exclude": ("image",)}, id="without_image"),
        pytest.param({}, id="full_news"),
    ])
    def test_create(self, faker, params, login):
        with allure.step("Получаем токен авторизации"):
            token = login(**USERS[0])
            self.headers = {"Authorization": f"Bearer {token}"}

        news_data = create_news(faker, params)
        files = make_files(news_data)

        response = requests.post(self.news_url, headers=self.headers, files=files)
        assert response.status_code == 200

        with allure.step("Проверка созданной новости"):
            created_news = NewsResponse(**response.json())

            assert created_news.title == news_data.title, "Заголовок не совпадает или отсутствует"
            assert created_news.text == news_data.text, "Текст не совпадает или отсутствует"

            if news_data.subtitle:
                assert created_news.subtitle == news_data.subtitle, "Подзаголовок не совпадает"

            if news_data.tags:
                tags = news_data.tags.split(", ")
                assert all(t.name in tags for t in created_news.tags), "Теги не совпадают"

            if news_data.image:
                assert created_news.image_path is not None, "Картинка не загрузилась"

    @allure.story("Проверка получения всех новостей")
    def test_get_all(self):
        response = requests.get(self.news_url)

        assert response.status_code == 200, "Ошибка получения новостей"
        assert response.json().get("items") is not None, "Нет списка"

    @allure.story("Получение тегов")
    def test_get_tags(self):
        response = requests.get(f"{self.news_url}tags")

        assert response.status_code == 200, "Ошибка получения тегов"
        result = response.json()

        assert isinstance(result, list)
        assert len(result) > 0

    @allure.story("Получение конкретной новости")
    def test_get_news(self, temp_news):
        response = temp_news

        example = NewsResponse(**response.json())

        response = requests.get(f"{self.news_url}{example.id}")

        assert response.status_code == 200
        received = NewsResponse(**response.json())

        assert received == example, "Полученная новость отличается от созданной"


    @allure.story("Проверка пагинации")
    def test_paginate(self):
        with allure.step("Получаем 1ю страницу"):
            response = requests.get(self.news_url, params={"page": 1, "per_page": 20})
            assert response.status_code == 200

            result = response.json()

            assert result["page"] == 1
            assert result["per_page"] == 20

            page1 = result["items"]

        with allure.step("Получаем 2ю страницу"):
            response = requests.get(self.news_url, params={"page": 2, "per_page": 20})
            assert response.status_code == 200

            result = response.json()

            assert result["page"] == 2
            assert result["per_page"] == 20

            page2 = response.json()["items"]

        with allure.step("Проверяем, что новости не повторяются"):
            assert all(page1[i] != page2[i] for i in range(20))

    @allure.story("Проверка поиска по тексту")
    def test_search_per_text(self, temp_news):
        import random

        with allure.step("Получаем созданную временную новость и фрагментированный текст"):
            news_data = temp_news.json()
            text_fragment = news_data["text"].split()

        with allure.step("Проверяем поиск по тексту"):
            word = text_fragment[random.randint(0, len(text_fragment) - 1)]
            response = requests.get(self.news_url, params={"search": word})

            assert response.status_code == 200

            assert any(news_data["id"] == n["id"] for n in response.json()["items"])

    @allure.story("Проверка поиска по тегу")
    def test_search_per_tag(self, temp_news):
        import random

        with allure.step("Получаем созданную временную новость и список тегов"):
            news_data = temp_news.json()
            tags = [t["name"] for t in news_data["tags"]]

        with allure.step("Проверяем поиск по тексту"):
            word = tags[random.randint(0, len(tags) - 1)]
            response = requests.get(self.news_url, params={"tag": word})

            assert response.status_code == 200

            assert any(news_data["id"] == n["id"] for n in response.json()["items"])
