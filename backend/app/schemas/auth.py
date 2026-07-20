from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombres: str
    apellidos: str
    correo: str
    estado: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    id_rol: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None
    estado: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
