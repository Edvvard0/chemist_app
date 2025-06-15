from pydantic import BaseModel, EmailStr


class SUser(BaseModel):
    id: int
    name: str


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    password: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str