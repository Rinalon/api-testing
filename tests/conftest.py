import pytest
import requests
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
        user = LoginModel(
            username=email,
            password=password,
        )
        response = requests.post(login_url, data=user.model_dump())

        return response.json().get("access_token")
    return __login