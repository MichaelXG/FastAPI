import uvicorn
import os
import pyodbc, struct 
# from azure import identity
from fastapi import FastAPI
from models.Usuarios import Usuarios
from http import HTTPStatus
    
connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]

app = FastAPI(title='API de Usuários')

# @app.get("/")
# def root():
#     try:
#         conn = get_conn()
#         cursor = conn.cursor()

#         # Table should be created ahead of time in production app.
#         cursor.execute("""
#            CREATE TABLE Usuario (
#                   CodigoUsuario			INT NOT NULL IDENTITY(1, 1)
#                 , CodigoEmpresa			INT NOT NULL 
#                 , NomeUsuario			VARCHAR(80) NOT NULL
#                 , Apelido				VARCHAR(40) NOT NULL
#                 , Password				VARCHAR(14) NOT NULL
#                 , CPF					VARCHAR(11) NOT NULL
#                 , Email					VARCHAR(80) NOT NULL
#                 , Telefone				VARCHAR(10) NULL
#                 , Celular				VARCHAR(11) NOT NULL
#                 , Ativo					BIT			NOT NULL CONSTRAINT DF_Usuario_Ativo DEFAULT 1
#                 , CodigoGrupoUsuario	INT			NOT NULL
#                 , InseridoPor			INT			NOT NULL
#                 , InseridoEm			DATETIME	NOT NULL CONSTRAINT DF_Usuario_InseridoEm DEFAULT GETDATE()
#                 , ModificadoPor			INT			NULL 
#                 , ModificadoEm			DATETIME	NULL
#                 , CONSTRAINT PK_Usuario_CodigoUsuario			PRIMARY KEY CLUSTERED (CodigoUsuario)
#                 , CONSTRAINT FK_Usuario_Usuario_InseridoPor		FOREIGN KEY (InseridoPor)	REFERENCES Usuario(CodigoUsuario)
#                 , CONSTRAINT FK_Usuario_Usuario_ModificadoPor	FOREIGN KEY (ModificadoPor)	REFERENCES Usuario(CodigoUsuario)
#                 , CONSTRAINT FK_Empresa_Usuario_CodigoEmpresa	FOREIGN KEY (CodigoEmpresa)	REFERENCES Empresa(CodigoEmpresa)
#                 , CONSTRAINT UNQ_Usuario_CPF					UNIQUE(CPF)
#                 )
#         """)

#         conn.commit()
#     except Exception as e:
#         # Table may already exist
#         print(e)
#     return "Usuário API"

@app.get("/Usuarios")
# ''' Lista todos dos Usuários cadastrados'''
def get_Usuarios():
    usuarios = []
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WITH(NOLOCK)")

        for usuario in cursor.fetchall():
            print(usuario.CodigoEmpresa, usuario.NomeUsuario, usuario.Apelido, usuario.Password, usuario.CPF, usuario.Email, usuario.Telefone, usuario.Celular, usuario.Ativo, usuario.CodigoGrupoUsuario, usuario.InseridoPor, usuario.InseridoEm, usuario.ModificadoPor, usuario.ModificadoEm)   
            usuarios.append(f"{usuario.CodigoUsuario}, {usuario.CodigoEmpresa}, {usuario.NomeUsuario}, {usuario.Apelido}, {usuario.Password}, {usuario.CPF}, {usuario.Email}, {usuario.Telefone}, {usuario.Celular}, {usuario.Ativo}, {usuario.CodigoGrupoUsuario}, {usuario.InseridoPor}, {usuario.InseridoEm}, {usuario.ModificadoPor}, {usuario.ModificadoEm}")
    return usuarios

@app.get("/Usuarios/{CodigoUsuario}")
def get_User_CodigoUsuario(CodigoUsuario: int):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WITH(NOLOCK) WHERE CodigoUsuario = ?", CodigoUsuario)

        usuario = cursor.fetchone()
        return f"{usuario.CodigoUsuario}, {usuario.CodigoEmpresa}, {usuario.NomeUsuario}, {usuario.Apelido}, {usuario.Password}, {usuario.CPF}, {usuario.Email}, {usuario.Telefone}, {usuario.Celular}, {usuario.Ativo}, {usuario.CodigoGrupoUsuario}, {usuario.InseridoPor}, {usuario.InseridoEm}, {usuario.ModificadoPor}, {usuario.ModificadoEm}"

@app.post("/Usuarios", status_code=HTTPStatus.CREATED)
def create_User(usuario: Usuarios):
    with get_conn() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO Usuario (CodigoEmpresa, NomeUsuario, Apelido, Password, CPF, Email, Telefone, Celular, Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm) \
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", usuario.CodigoEmpresa, usuario.NomeUsuario, usuario.Apelido, usuario.Password, usuario.CPF, usuario.Email, usuario.Telefone, usuario.Celular, usuario.Ativo, usuario.CodigoGrupoUsuario, usuario.InseridoPor, usuario.InseridoEm, None, None)
        except Exception as e:
            print("Erro:", str(e))
            cursor.rollback()
            cursor.close()
            return False
        else:
            conn.commit()

    return True

def get_conn():
    # credential = identity.DefaultAzureCredential(exclude_interactive_busuarioser_credential=False)
    # token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    # token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    # SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    # conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    conn = pyodbc.connect(connection_string)
    return conn

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)