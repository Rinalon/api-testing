from pydantic import BaseModel, EmailStr, Field, validator

class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")

class Body_login_api_auth_login_post(BaseModel):
    grant_type: str | None = None
    username: str
    password: str
    scope: str | None = Field(default="")
    client_id: str | None =  None
    client_secret: str | None = None


if __name__ == "__main__":
    Body_login_api_auth_login_post(
        username = "",
        password = "",
    )