import pytest
import allure
import requests
from models import CommentResponse, CommentCreate, Body_create_news_api_news_post as NewsCreate
from helpers import generate_user, generate_news
from tests.conftest import BASE_URL, USERS
from datetime import date

class TestComments:
    @pytest.fixture(autouse=True)
    def setup(self, login, faker):
        with allure.step("Получаем токен авторизации"):
            token = login(**USERS[0])
            headers = {"Authorization": f"Bearer {token}"}

        with allure.step("Создание новости"):
            news_data = NewsCreate(**generate_news(faker, exclude=("image"), tags_is_list=True))
            response = requests.post(f"{BASE_URL}/api/news", headers=headers, json=news_data.model_dump())
            self.news_id = response.json().get("id")

        with allure.step("Выполнение теста"):
            yield self.news_id

        with allure.step("Очистка"):
            # 403
            response = requests.delete(f"{BASE_URL}/api/admin/news/{self.news_id}", headers=headers)

    def __get_comments_url(self, news_id):
        return  f"{BASE_URL}/api/news/{news_id}/comments"

    def __get_comments(self, news_id):
        return requests.get(self.__get_comments_url(news_id)).json()

    def test_add_comment(self, faker, login):
        with allure.step("Получаем токен авторизации"):
            token = login(**USERS[0])
            headers = {"Authorization": f"Bearer {token}"}

        with allure.step("Генерируем url и комментарий"):
            url = self.__get_comments_url(self.news_id)

            text = faker.text()
            comment = CommentCreate(text=text)

        with allure.step("Отправляем запрос"):
            response = requests.post(url, json=comment.model_dump(), headers=headers)

            assert response.status_code == 200, f"Ошибка выполнения: {response.status_code}, \n{response.json}"

        with allure.step("Проверяем наличие"):
            comment_id = response.json().get("id")
            comments = self.__get_comments(self.news_id)

            assert any((c.id == comment_id
                        and c.text==text
                        and c.created_at.date == date.today()
                        ) for c in comments), "Комментарий не найден"


    def test_get_comments(self):
        pass