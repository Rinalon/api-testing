import pytest
import allure
from models import CommentResponse, CommentCreate
from tests.conftest import create_news

class TestComments:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client, faker):
        self.faker = faker
        self.api_client = auth_client

    @allure.step("Создание url для подключения")
    def __get_comments_endpoint(self, news_id):
        return  f"/api/news/{news_id}/comments"

    @allure.step("Получение комментариев к новости")
    def __get_comments(self, news_id):
        response = self.api_client.get(self.__get_comments_endpoint(news_id))

        return [CommentResponse(**c) for c in response.json()]

    @allure.step("Создание комментариев")
    def __create_comments(
            self,
            news_id: int,
            count: int | None = 1,
    ):
        endpoint = self.__get_comments_endpoint(news_id)
        comments = []

        for _ in range(count):
            with allure.step("Генерируем комментарий"):
                comment = CommentCreate(text=self.faker.text())

            with allure.step("Создаём комментарий"):
                response = self.api_client.post(endpoint, json=comment.model_dump())

                comments.append(CommentResponse(**response.json()))
        return comments

    def test_add(self):
        news = create_news(self.faker, self.api_client, {"exclude": ("image",)})
        news_id = news["id"]
        created = self.__create_comments(news_id, count = 1)

        with allure.step("Проверяем наличие комментария"):
            comment = created[0]
            comments = self.__get_comments(news_id)

            assert any(c == comment for c in comments), "Комментарий не найден"

    def test_get(self):
        count = 10
        news = create_news(self.faker, self.api_client, {"exclude": ("image",)})
        news_id = news["id"]

        created = self.__create_comments(news_id, count=count)
        comments = self.__get_comments(news_id)

        with allure.step("Сортируем по id, чтобы гарантировать одинаковый порядок комментариев"):
            created.sort(key=lambda c: c.id)
            comments.sort(key=lambda c: c.id)

        assert all(comments[i] == created[i] for i in range(count)), "Комментарии не совпадают"