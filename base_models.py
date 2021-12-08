from pydantic import BaseModel
from typing import Optional


class Login(BaseModel):
    email: str
    password: str


class Registration(BaseModel):
    user_name: str = None
    email: str
    password: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
#     Todo: to check parameters, data come as "" not null


class UpdateUser(BaseModel):
    user_name: str
    address: Optional[str]
    phone_number: Optional[str]


class Passwords(BaseModel):
    current_password: str
    new_password: str






