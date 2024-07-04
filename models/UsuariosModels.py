from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from services.database import Base

class UsuarioModels(Base):
    __tablename__ = 'Usuario'

    CodigoUsuario = Column(Integer, primary_key=True, autoincrement=True)
    CodigoEmpresa = Column(Integer)
    NomeUsuario = Column(String)
    Apelido = Column(String)
    Password = Column(String)
    CPF = Column(String)
    Email = Column(String)
    Telefone = Column(String)
    Celular = Column(String)
    Ativo = Column(Boolean, default=True)
    CodigoGrupoUsuario = Column(Integer)
    InseridoPor = Column(Integer)
    InseridoEm = Column(DateTime, default=datetime.utcnow)
    ModificadoPor = Column(Integer)
    ModificadoEm = Column(DateTime)
