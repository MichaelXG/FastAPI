from pydantic import BaseModel, Field

class Usuarios(BaseModel):
    CodigoEmpresa      : int
    NomeUsuario        : str | None = None
    Apelido            : str | None = None
    Password           : str | None = None
    CPF                : str | None = None
    Email              : str | None = None
    Telefone           : str | None = None
    Celular            : str | None = None
    Ativo              : bool
    CodigoGrupoUsuario : int
    InseridoPor        : int
    InseridoEm         : str 
    ModificadoPor      : int
    ModificadoEm       : str | None = None