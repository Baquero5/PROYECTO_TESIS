from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    id_rol: int
    nombres: str
    apellidos: str
    correo: str
    password: str


class UserLogin(BaseModel):
    correo: str
    password: str


class UserResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombres: str
    apellidos: str
    correo: str
    estado: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
