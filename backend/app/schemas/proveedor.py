from pydantic import BaseModel
from typing import Optional


class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None


class ProveedorResponse(BaseModel):
    id_proveedor: int
    razon_social: str
    ruc: str
    telefono: Optional[str]
    correo: Optional[str]
    direccion: Optional[str]

    class Config:
        from_attributes = True
