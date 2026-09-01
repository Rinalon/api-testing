import pytest
import requests
from models import UserCreate, Body_login_api_auth_login_post as LoginModel
from helpers import generate_user
from tests.conftest import BASE_URL, USERS
from datetime import date

# TODO: организовать фикстуры для очистки

class TestAuth:
    register_url = BASE_URL + '/api/auth/register'
    login_url = BASE_URL + '/api/auth/login'

    def __create_user(self, user):
        return requests.post(self.register_url, json=user.model_dump())

    def __delete_user(self, user_id):
        return requests.delete(f"{BASE_URL}/api/admin/users/{user_id}")

    @pytest.fixture()
    def cleanup(self):
        pass

    @pytest.mark.positive
    def test_register_success(self, faker):
        user = UserCreate(**generate_user(faker))

        response = requests.post(self.register_url, json=user.model_dump())

        assert response.status_code == 200

        created_user = response.json()

        assert created_user["created_at"][:10] == date.today().isoformat()
        assert user == UserCreate(
            password=user.password, # т.к. нет в возвращаемом json
            **created_user
        )

        #cleanup
        user_id = created_user["id"]
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}")

    @pytest.mark.negative
    def test_register_same_email_fail(self, faker):
        user = UserCreate(**generate_user(faker))

        response = requests.post(self.register_url, json=user.model_dump())
        assert response.status_code == 200

        user_id = response.json()["id"]

        response = requests.post(self.register_url, json=user.model_dump())
        assert response.status_code == 400

        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}")

    @pytest.mark.parametrize("param", [

    ])
    def test_register_invalid_data(self, faker, param):
        pass

    @pytest.mark.positive
    def test_login_success(self):
        user = LoginModel(
            username=USERS[0]["email"],
            password=USERS[0]["password"],
        )
        response = requests.post(self.login_url, data=user.model_dump())

        assert response.status_code == 200

    @pytest.mark.negative
    def test_login_fail(self, faker):

        raw_user = generate_user(faker,
                exclude=("first_name, last_name", "phone"))

        user = LoginModel(
            username=raw_user["email"],
            password=raw_user["password"],
        )

        response = requests.post(self.login_url, data=user.model_dump())

        assert response.status_code == 422



