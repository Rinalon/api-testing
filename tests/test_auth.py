import pytest
import allure
from models import UserCreate, Body_login_api_auth_login_post as LoginModel
from helpers import generate_user
from datetime import date

@allure.epic("Auth")
class TestAuth:
    reg_endpoint = '/api/auth/register'
    login_endpoint = '/api/auth/login'

    @pytest.fixture(autouse=True)
    def setup(self, faker, api_client):
        """Фикстура для инициализации"""
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

    @allure.feature("Регистрация")
    @allure.story("Позитивный тест на регистрацию")
    @allure.description("""
        1 Создаём пользователя
        2 Регистрируем
        3 Проверяем дату создания и данные аккаунта
    """)
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

    @allure.feature("Регистрация")
    @allure.story("Негативный тест на регистрацию")
    @allure.description("""
        1 Создаём пользователя
        2 Регистрируем
        3 Пытаемся зарегистрировать во 2й раз
    """)
    @pytest.mark.negative
    def test_register_same_email_fail(self):
        raw_user = self.__create_user()

        self.__registrate_user(raw_user)

        with allure.step("Повторяем попытку регистрации"):
            self.__registrate_user(raw_user, expected_status=400)

    @allure.feature("Логин")
    @allure.story("Позитивный тест на вход")
    @allure.description("""
        1 Берём данные пользователя, который уже существует в системе
        2 Входим
    """)
    @pytest.mark.positive
    def test_login_success(self, test_user_credentials):
        with allure.step("Берём данные пользователя, который точно существует в системе"):
            user = LoginModel(**test_user_credentials)

        self.__login(user)

    @allure.feature("Логин")
    @allure.story("Негативный тест на регистрацию")
    @allure.description("""
        1 Создаём email и пароль
        2 Пытаемся войти
    """)
    @pytest.mark.negative
    def test_login_fail(self, faker):
        with allure.step("Создаём email и пароль, которых ранее в системе точно не было"):
            from datetime import datetime

            user = LoginModel(
                email=f"test_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{faker.email()}",
                password=faker.password(length=10, special_chars=True, digits=True),
            )

        self.__login(user, expected_status=422)

    @allure.feature("Регистрация")
    @allure.story("Проверка регистрации с невалидными данными")
    @allure.description("""
        1 Создаём пользователя без почты
        2 Ставим почту из параметра теста
        3 Пытаемся зарегистрировать
        
        Т.к. Pydantic-модель упадёт с ValidationError, в тесте она не используется
    """)
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

    @allure.feature("Регистрация")
    @allure.story("Проверка регистрации разными паролями")
    @allure.description("""
        1 Создаём пользователя без пароля
        2 Ставим пароль из параметра теста
        3 Пытаемся зарегистрировать

        Т.к. Pydantic-модель упадёт с ValidationError, в тесте она не используется
    """)
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
