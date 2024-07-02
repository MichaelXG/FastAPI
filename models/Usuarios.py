from pydantic import BaseModel, conint, constr, validator
from typing import Optional
from datetime import datetime

class Usuarios(BaseModel):
    CodigoEmpresa       : conint(ge=1) # type: ignore
    NomeUsuario         : constr(strip_whitespace=True, min_length=1, max_length=255) # type: ignore
    Apelido             : constr(strip_whitespace=True, min_length=1, max_length=40) # type: ignore
    Password            : constr(strip_whitespace=True, min_length=6, max_length=14) # type: ignore
    CPF                 : constr(strip_whitespace=True, min_length=11, max_length=11) # type: ignore
    Email               : constr(strip_whitespace=True, max_length=80) # type: ignore
    Telefone            : Optional[constr(strip_whitespace=True, min_length=10, max_length=10)] = None # type: ignore
    Celular             : constr(strip_whitespace=True, min_length=11, max_length=11) # type: ignore
    Ativo               : bool
    CodigoGrupoUsuario  : conint(ge=1) # type: ignore
    InseridoPor         : conint(ge=1) # type: ignore
    InseridoEm          : datetime
    ModificadoPor       : Optional[conint(ge=1)] = None # type: ignore
    ModificadoEm        : Optional[datetime] = None

    class Config:
        orm_mode = True

    @validator("CPF")
    def validate_cpf(cls, value):
        if not value.isdigit() or len(value) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos.")
        return value

# class UpdateUsuarios(BaseModel):
#     CodigoEmpresa       : Optional[conint(ge=1)] # type: ignore
#     NomeUsuario         : Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] # type: ignore
#     Apelido             : Optional[constr(strip_whitespace=True, min_length=1, max_length=40)] # type: ignore
#     Password            : Optional[constr(strip_whitespace=True, min_length=6, max_length=14)] # type: ignore
#     CPF                 : Optional[constr(strip_whitespace=True, min_length=11, max_length=11)] # type: ignore
#     Email               : Optional[constr(strip_whitespace=True, max_length=80)] # type: ignore
#     Telefone            : Optional[constr(strip_whitespace=True, min_length=10, max_length=10)] = None # type: ignore
#     Celular             : Optional[constr(strip_whitespace=True, min_length=11, max_length=11)] # type: ignore
#     Ativo               : Optional[bool]
#     CodigoGrupoUsuario  : Optional[conint(ge=1)] # type: ignore
#     ModificadoPor       : conint(ge=1) # type: ignore
#     ModificadoEm        : datetime

#     class Config:
#         orm_mode = True

#     @validator("CPF", always=True)
#     def validate_cpf(cls, value):
#         if value and (not value.isdigit() or len(value) != 11):
#             raise ValueError("CPF deve conter exatamente 11 dígitos.")
#         return value
