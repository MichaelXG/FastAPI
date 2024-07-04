from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UsuarioCreate(BaseModel):
    CodigoEmpresa: int
    NomeUsuario: str
    Apelido: str
    Password: str
    CPF: str
    Email: str
    Telefone: str
    Celular: str
    Ativo: bool
    CodigoGrupoUsuario: int
    InseridoPor: int
    InseridoEm: datetime

class UsuarioOut(BaseModel):
    CodigoUsuario: int
    CodigoEmpresa: int
    NomeUsuario: str
    Apelido: str
    Password: str
    CPF: str
    Email: str
    Telefone: str
    Celular: str
    Ativo: bool
    CodigoGrupoUsuario: int
    InseridoPor: int
    InseridoEm: datetime
    ModificadoPor: Optional[int]
    ModificadoEm: Optional[datetime]

    class Config:
        orm_mode = True
