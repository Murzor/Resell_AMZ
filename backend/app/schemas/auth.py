from pydantic import BaseModel


class Login(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

