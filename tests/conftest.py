import pytest
import allure
import requests
from helpers import generate_user, generate_news
from models import Body_create_news_api_news_post as NewsCreate
from faker import Faker

BASE_URL = "https://archiscope.ru"

# Данные тестовых пользователей
USERS = [
        {"email": "test@example.com", "password": "password123"},
        {"email": "example@example.com", "password": "123pass456"},
]

@pytest.fixture(scope="session")
def faker():
    return Faker("ru_RU")

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def requests_session(base_url):
    class Session():
        def __init__(self, base_url):
            self.base_url = base_url

        def request(self, method, url, **kwargs): pass

        def post(self):
            pass
    return requests.Session()
#TODO фикстура-обёртка над реквестом

#Это надо будет засунуть в storage или общую фикстуру
@pytest.fixture(scope="function")
def login():
    def __login(email, password):
        from models import Body_login_api_auth_login_post as LoginModel

        login_url = BASE_URL + '/api/auth/login'
        user = LoginModel(email=email, password=password)
        response = requests.post(login_url, data=user.model_dump())

        return response.json().get("access_token")
    return __login

@allure.step("Подготовка данных для запроса")
def make_files(news_data):
    import os
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

    return files

@allure.step("Создание новости")
def create_news(faker, params):
    news_data = NewsCreate(**generate_news(faker, **params))
    return news_data

@pytest.fixture(scope="function")
def temp_news(request, faker, login):
    with allure.step("Логинимся под админом"):
        token = login(**USERS[0])
        headers = {"Authorization": f"Bearer {token}"}

    with allure.step("Создаём новость"):
        news_data = create_news(faker=faker, params={"exclude": ("image",)})
        files = make_files(news_data)

        response = requests.post(f"{BASE_URL}/api/news/", headers=headers, files=files)
        news_id = response.json().get("id")

    yield response

    with allure.step("Удаляем"):
        #403
        requests.delete(f"{BASE_URL}/api/news/{news_id}", headers=headers)