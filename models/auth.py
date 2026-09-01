from pydantic import BaseModel, EmailStr, Field, validator

class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")

class Body_login_api_auth_login_post(BaseModel):
    grant_type: str | None
    username: str
    password: str
    scope: str = Field(default="")
    client_id: str | None
    client_secret: str | None