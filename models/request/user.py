from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class PasswordUpdate(BaseModel):
    password: str


class ResendEmail(BaseModel):
    email: str


class EmailVerificationRequest(BaseModel):
    email: str
    code: int