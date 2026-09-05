import pytest
import allure
import requests
from models import NewsResponse, Body_create_news_api_news_post as NewsCreate
from tests.conftest import create_news
from helpers import make_files, generate_news

class TestNews:
    news_endpoint = "/api/news/"

    @pytest.fixture(autouse=True)
    def setup(self, auth_client, faker):
        self.api_client = auth_client
        self.faker = faker

    @allure.story("Проверка создания новости")
    @pytest.mark.parametrize("params", [
        pytest.param({"exclude": ("image",)}, id="without_image"),
        pytest.param({}, id="full_news"),
    ])
    def test_create(self, params):
        news_data = NewsCreate(**generate_news(self.faker, **params))
        files = make_files(news_data)

        response = self.api_client.post(self.news_endpoint, files=files)

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
        response = self.api_client.get(self.news_endpoint)

        assert response.json().get("items") is not None, "Нет списка"

    @allure.story("Получение тегов")
    def test_get_tags(self):
        response = self.api_client.get(f"{self.news_endpoint}tags")

        result = response.json()

        assert isinstance(result, list)
        assert len(result) > 0

    @allure.story("Получение конкретной новости")
    def test_get_news(self):
        news_data = create_news(faker=self.faker, api_client=self.api_client)
        example = NewsResponse(**news_data)

        with allure.step("Получение созданной новости"):
            response = self.api_client.get(f"{self.news_endpoint}{example.id}")
            received = NewsResponse(**response.json())

        assert received == example, "Полученная новость отличается от созданной"

    @allure.story("Проверка пагинации")
    def test_paginate(self):
        with allure.step("Получаем 1ю страницу"):
            response = self.api_client.get(self.news_endpoint, params={"page": 1, "per_page": 20})
            result = response.json()

            assert result["page"] == 1
            assert result["per_page"] == 20

            page1 = result["items"]

        with allure.step("Получаем 2ю страницу"):
            response = self.api_client.get(self.news_endpoint, params={"page": 2, "per_page": 20})
            result = response.json()

            assert result["page"] == 2
            assert result["per_page"] == 20

            page2 = response.json()["items"]

        with allure.step("Сортируем новости на страницах, чтобы гарантировать порядок для сравнения"):
            page1.sort(key=lambda x: x["created_at"], reverse=True)
            page2.sort(key=lambda x: x["created_at"], reverse=True)

        with allure.step("Проверяем, что новости не повторяются"):
            assert all(page1[i] != page2[i] for i in range(20))

    @allure.story("Проверка поиска по тексту")
    def test_search_per_text(self):
        import random

        with allure.step("Получаем созданную временную новость и фрагментированный текст"):
            news_data = create_news(self.faker, self.api_client)
            text_fragment = news_data["text"].split()

        with allure.step("Проверяем поиск по тексту"):
            word = text_fragment[random.randint(0, len(text_fragment) - 1)]
            response = self.api_client.get(self.news_endpoint, params={"search": word})

            assert any(news_data["id"] == n["id"] for n in response.json()["items"])

    @allure.story("Проверка поиска по тегу")
    def test_search_per_tag(self):
        import random

        with allure.step("Получаем созданную временную новость и список тегов"):
            news_data = create_news(self.faker, self.api_client)
            tags = [t["name"] for t in news_data["tags"]]

        with allure.step("Проверяем поиск по тексту"):
            word = tags[random.randint(0, len(tags) - 1)]
            response = self.api_client.get(self.news_endpoint, params={"tag": word})

            assert any(news_data["id"] == n["id"] for n in response.json()["items"])
