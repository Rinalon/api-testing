import pytest
import allure
import requests
from models import CommentResponse, CommentCreate
from tests.conftest import BASE_URL, USERS

class TestComments:
    @pytest.fixture(autouse=True)
    def setup(self, login):
        token = login(**USERS[1])
        self.headers = {"Authorization": f"Bearer {token}"}

    @allure.step("Создание url для подключения")
    def __get_comments_url(self, news_id):
        return  f"{BASE_URL}/api/news/{news_id}/comments"

    @allure.step("Получение комментариев к новости")
    def __get_comments(self, news_id):
        response = requests.get(self.__get_comments_url(news_id))
        assert response.status_code == 200, f"Ошибка выполнения: {response.status_code}, \n{response.json}"

        return [CommentResponse(**c) for c in response.json()]

    @allure.step("Создание комментария")
    def __create_comments(
            self,
            faker,
            news_id: int,
            count: int | None = 1,
    ):
        with allure.step("Генерируем url"):
            url = self.__get_comments_url(news_id)

        comments = []
        for _ in range(count):
            with allure.step("Генерируем комментарий"):
                comment = CommentCreate(text=faker.text())

            with allure.step("Создаём комментарий"):
                response = requests.post(url, json=comment.model_dump(), headers=self.headers)
                assert response.status_code == 200, f"Ошибка выполнения: {response.status_code}, \n{response.json}"

                comments.append(CommentResponse(**response.json()))
        return comments

    def test_add(self, faker, temp_news):
        news_id = temp_news.json().get("id")

        created = self.__create_comments(faker, news_id, count = 1)

        with allure.step("Проверяем наличие комментария"):
            comment = created[0]
            comments = self.__get_comments(news_id)

            assert any(c == comment for c in comments), "Комментарий не найден"

    def test_get(self, faker, temp_news):
        count = 10
        news_id = temp_news.json().get("id")


        created = self.__create_comments(faker, news_id, count=count)
        comments = self.__get_comments(news_id)

        with allure.step("Сортируем по id, чтобы гарантировать одинаковый порядок комментариев"):
            created.sort(key=lambda c: c.id)
            comments.sort(key=lambda c: c.id)

        assert all(comments[i] == created[i] for i in range(count)), "Комментарии не совпадают"