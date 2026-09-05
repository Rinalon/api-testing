import pytest
import allure
import requests
from helpers import generate_news, make_files
from models import (
    Token, UserResponse,
    Body_create_news_api_news_post as NewsCreate,
    Body_login_api_auth_login_post as LoginModel
)
from faker import Faker

@pytest.fixture(scope="session")
def faker():
    return Faker("ru_RU")

@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://archiscope.ru"

@pytest.fixture(scope="session")
def test_user_credentials() -> dict[str, str]:
    return {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Tester",
        "last_name": "Tester",
    }

@pytest.fixture(scope="session")
def api_client(base_url: str, test_user_credentials: dict[str, str]):
    class APIClient:
        def __init__(self) -> None:
            self.base_url = base_url
            self.test_user_credentials = test_user_credentials

            self.session = requests.Session()

            self.token = None

        def set_token(self, token):
            self.token = token
            self.session.headers.update({"Authorization": f"Bearer {token}"})

        def _get_header(self):
            headers = {"Content-Type": "application/json"}
            return headers

        def request(
                self,
                method: str,
                endpoint: str,
                expected_status: int | None = 200,
                **kwargs
        ):
            url = f"{self.base_url}{endpoint}"

            response = self.session.request(method, url, **kwargs)

            assert response.status_code == expected_status, (
                f"При запросе {url} ожидалось {expected_status}, получено {response.status_code}, {response.json()}"
            )
            return response

        def get(self, endpoint: str, expected_status: int | None = 200, **kwargs):
            return self.request("GET", endpoint, expected_status, **kwargs)

        def post(self, endpoint: str, expected_status: int | None = 200, **kwargs):
            return self.request("POST", endpoint, expected_status, **kwargs)

    return APIClient()

@pytest.fixture(scope="session")
def auth_client(api_client, test_user_credentials: dict[str, str]):
    login_data = LoginModel(**test_user_credentials)

    response = api_client.post(
        "/api/auth/login",
                data=login_data.model_dump(),
                expected_status=200,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    token = Token(**response.json())
    api_client.set_token(token.access_token)

    user_response = api_client.get("/api/user/me", expected_status=200)

    return api_client

@pytest.fixture(scope="function")
def cleanup(faker, auth_client):
    def __cleanup(endpoint: str):
        with allure.step("Удаляем"):
            # 403 т.к. нет данных от админа
            auth_client.request("DELETE", endpoint, expected_status=403)
    return __cleanup

# Здесь, т.к. нужна в 2х классах
@allure.step("Создание новости")
def create_news(faker, api_client, params: dict | None = {}):
    news_data = NewsCreate(**generate_news(faker, **params))
    files = make_files(news_data)

    response = api_client.post("/api/news/", files=files)
    return response.json()