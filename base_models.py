from pydantic import BaseModel
from typing import Optional, List, Dict


class Login(BaseModel):
    email: str
    password: str


class Registration(BaseModel):
    user_name: str = None
    email: str
    password: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    zip_code: Optional[str] = None
    city: str


# Todo: to check parameters, data come as "" not null


class UpdateUser(BaseModel):
    user_name: str
    address: Optional[str]
    phone_number: Optional[str]
    zip_code: Optional[str]
    city: str


class Passwords(BaseModel):
    current_password: str
    new_password: str


class BookId(BaseModel):
    book_id: str


class OrderList(BaseModel):
    book_id: str
    book_image: str
    book_name: str
    book_author: str
    supplier_name: str
    supplier_book_id: int
    total: str
    post: str


class Order(BaseModel):
    order: List[OrderList]


class UpdateOrder(BaseModel):
    id: str
    status: str
