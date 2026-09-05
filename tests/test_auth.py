import pytest
import allure
import requests
from models import UserCreate, Body_login_api_auth_login_post as LoginModel, UserResponse
from helpers import generate_user
from datetime import date

class TestAuth:
    reg_endpoint = '/api/auth/register'
    login_endpoint = '/api/auth/login'

    @pytest.fixture(autouse=True)
    def setup(self, faker, api_client):
        self.faker = faker
        self.api_client = api_client

    @allure.step("Создам пользователя")
    def __create_user(self, **kwargs):
        return UserCreate(**generate_user(self.faker, **kwargs))

    @allure.step("Регистрируем пользователя")
    def __registrate_user(self, user: UserCreate | dict, expected_status: int | None = 200):
        user = user.model_dump() if isinstance(user, UserCreate) else user

        request = self.api_client.post(
            endpoint=self.reg_endpoint,
            expected_status=expected_status,
            json=user
        )
        return request.json()

    @allure.step("Входим в систему")
    def __login(self, user: LoginModel, expected_status: int | None = 200):
        return self.api_client.post(
            endpoint=self.login_endpoint,
            expected_status=expected_status,
            data=user.model_dump(),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    @pytest.mark.positive
    def test_register_success(self):
        raw_user = self.__create_user()
        created_user = self.__registrate_user(raw_user)

        with allure.step("Проверяем данные созданного пользователя"):
            assert created_user["created_at"][:10] == date.today().isoformat(), "Не совпала дата создания"

            raw_user = raw_user.model_dump()
            common_keys = set(raw_user.keys()) & set(created_user.keys())
            for key in common_keys:
                assert raw_user[key] == created_user[key], f"Не совпало поле {key}"

    @pytest.mark.negative
    def test_register_same_email_fail(self):
        raw_user = self.__create_user()

        self.__registrate_user(raw_user)

        with allure.step("Повторяем попытку регистрации"):
            self.__registrate_user(raw_user, expected_status=400)

    @pytest.mark.positive
    def test_login_success(self, test_user_credentials):
        with allure.step("Берём данные пользователя, который точно существует в системе"):
            user = LoginModel(**test_user_credentials)

        self.__login(user)

    @pytest.mark.negative
    def test_login_fail(self, faker):
        with allure.step("Создаём email и пароль, которых ранее в системе точно не было"):
            from datetime import datetime

            user = LoginModel(
                email=f"test_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{faker.email()}",
                password=faker.password(length=10, special_chars=True, digits=True),
            )

        self.__login(user, expected_status=422)

    @pytest.mark.negative
    @pytest.mark.parametrize("email", [
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
    ])
    def test_register_invalid_email(self, faker, email):
        with allure.step("Создаём пользователя"):
            user = generate_user(faker, exclude=("email",))
            user["email"] = email

        with allure.step("Пытаемся зарегистрировать"):
            self.__registrate_user(user, 422)

    @pytest.mark.parametrize("password, status_code", [
        pytest.param("12345", 422, id="too_small"),
        pytest.param("1a_B56", 200, id="correct_password"),
    ])
    def test_register_different_password(self, faker, password, status_code):
        with allure.step("Создаём пользователя"):
            user = generate_user(faker, exclude=("password",))
            user["password"] = password

        with allure.step("Пытаемся зарегистрировать"):
            self.__registrate_user(user, status_code)
