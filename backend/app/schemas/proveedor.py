from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class ProveedorCreate(BaseModel):
    razon_social: str = Field(..., min_length=2, max_length=200)
    ruc: str = Field(..., min_length=10, max_length=13)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = Field(None, max_length=300)

    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v):
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10 or len(digits) > 13:
            raise ValueError('El RUC debe tener entre 10 y 13 dígitos')
        return v

    @field_validator('correo')
    @classmethod
    def validate_correo(cls, v):
        if v is not None and v != '':
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Ingrese un correo electrónico válido')
        return v


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=2, max_length=200)
    ruc: Optional[str] = Field(None, min_length=10, max_length=13)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = Field(None, max_length=300)


class ProveedorResponse(BaseModel):
    id_proveedor: int
    razon_social: str
    ruc: str
    telefono: Optional[str]
    correo: Optional[str]
    direccion: Optional[str]

    class Config:
        from_attributes = True
