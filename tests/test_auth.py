import pytest
import allure
import requests
from models import UserCreate, Body_login_api_auth_login_post as LoginModel
from helpers import generate_user
from tests.conftest import BASE_URL, USERS
from datetime import date

@pytest.fixture(scope="function")
def temp_user(faker, login):
    with allure.step("Создаём пользователя"):
        user = UserCreate(**generate_user(faker))

        response = requests.post(f"{BASE_URL}/api/auth/register", json=user.model_dump())
        assert response.status_code == 200

        user_id = response.json()["id"]

    yield (user, response.json())

    with allure.step("Логинимся под админом"):
        token = login(**USERS[0])
        headers = {"Authorization": f"Bearer {token}"}

    with allure.step("Удаляем"):
        #403
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers)

class TestAuth:
    register_url = BASE_URL + '/api/auth/register'
    login_url = BASE_URL + '/api/auth/login'

    @pytest.mark.positive
    def test_register_success(self, temp_user):
        raw_user, created_user = temp_user

        with allure.step("Проверяем данные созданного пользователя"):
            assert created_user["created_at"][:10] == date.today().isoformat(), "Не совпала дата создания"

            raw_user = raw_user.model_dump()
            common_keys = set(raw_user.keys()) & set(created_user.keys())
            for key in common_keys:
                assert raw_user[key] == created_user[key], f"Не совпало поле {key}"

    @pytest.mark.negative
    def test_register_same_email_fail(self, temp_user):
        raw_user, created_user = temp_user

        with allure.step("Повторяем попытку регистрации"):
            response = requests.post(self.register_url, json=raw_user.model_dump())
            assert response.status_code == 422, f"Ожидалось 422, получено: {response.status_code}, {response.json()}"

    @pytest.mark.positive
    def test_login_success(self):
        with allure.step("Берём данные пользователя, который точно существует в системе"):
            user = LoginModel(**USERS[0])

        with allure.step("Пытаемся войти"):
            response = requests.post(self.login_url, data=user.model_dump())
            assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}, {response.json()}"

    @pytest.mark.negative
    def test_login_fail(self, faker):
        with allure.step("Создаём email и пароль, которых ранее в системе точно не было"):
            raw_user = generate_user(faker, exclude=("first_name, last_name", "phone",))

            user = LoginModel(
                email=raw_user["email"],
                password=raw_user["password"],
            )

        with allure.step("Пытаемся войти"):
            response = requests.post(self.login_url, data=user.model_dump())
            assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}, {response.json()}"

    @pytest.mark.negative
    @pytest.mark.parametrize("email", [
        # -------- Синтаксис и формат --------
        pytest.param("anna@anna", id="no_dot_in_tld"),
        pytest.param("anna@1example.com", id="domain_starts_with_digit"),
        pytest.param("example", id="no_at_sign"),
        pytest.param("1anna@anna.ru", id="local_part_starts_with_digit"),
        pytest.param("", id="empty"),
        pytest.param("   ", id="spaces_only"),
        pytest.param("anna @anna.ru", id="space_inside"),
        pytest.param("anna@@anna.ru", id="double_at"),
        pytest.param("anna.@anna.ru", id="dot_at_end_of_local"),
        pytest.param("anna@anna.ru.", id="domain_ends_with_dot"),
        pytest.param("anna@[192.168.1.1]", id="ip_as_domain"),
        pytest.param("anna!@test.com", id="invalid_special_char"),

        # -------- Длина --------
        pytest.param("a" * 250 + "@example.com", id="too_long"),

        # -------- Безопасность --------
        pytest.param("'; DROP TABLE users; --@test.com", id="sql_injection"),
        pytest.param("<script>alert('xss')</script>@test.com", id="xss_attempt"),
    ])
    def test_register_invalid_email(self, faker, email):
        with allure.step("Создаём пользователя"):
            user = generate_user(faker, exclude=("email",))
            user["email"] = email

        with allure.step("Пытаемся зарегистрировать"):
            response = requests.post(f"{BASE_URL}/api/auth/register", json=user)
            assert response.status_code == 422

    @pytest.mark.parametrize("password, status_code", [
        pytest.param("12345", 422, id="too_small"),
        pytest.param("1a_B56", 200, id="correct_password"),
    ])
    def test_register_different_password(self, faker, password, status_code):
        with allure.step("Создаём пользователя"):
            user = generate_user(faker, exclude=("password",))
            user["password"] = password

        with allure.step("Пытаемся зарегистрировать"):
            response = requests.post(f"{BASE_URL}/api/auth/register", json=user)
            assert response.status_code == status_code
