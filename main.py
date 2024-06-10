import os
import pyodbc
import struct
from fastapi import FastAPI, HTTPException
import uvicorn
from models.Usuarios import Usuarios
from http import HTTPStatus
import pandas as pd

# Atualize a string de conexão com a nova senha
connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]

app = FastAPI(title='API de Usuários')

def get_conn():
    try:
        conn = pyodbc.connect(connection_string)
        print("Conexão estabelecida com sucesso!")
        return conn
    except pyodbc.Error as e:
        print("Erro ao conectar ao banco de dados 01:", e)
        return None

@app.get("/Usuarios_all")
def get_Usuarios():
    usuarios = []
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados 02.")
    
    with conn:
        # Criar um cursor para executar consultas
        cursor = conn.cursor()
      
        try:
            comando_sql = f'SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario \
                                 , dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password \
                                 , dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) as Email, dbo.fn_Descriptografa(Telefone) as Telefone \
                                 , dbo.fn_Descriptografa(Celular) as Celular, Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm  \
                              FROM Usuario WITH(NOLOCK) '
            # Especificar as colunas que devem ser interpretadas como datas
            colunas_datas = ['InseridoEm', 'ModificadoEm']
            # Recuperar a próxima linha de resultados
            record = pd.read_sql(comando_sql, conn, parse_dates=colunas_datas)
            # Replace NaN values with None
            record = record.where(pd.notnull(record), None)
            # Converter o DataFrame em um dicionário
            record_dict = record.to_dict(orient='records')
         
        except Exception as e:
            print("Erro:", str(e))
            cursor.close()
            raise HTTPException(status_code=500, detail="Erro ao consultar o banco de dados.")
        else:
            new_record_dict = {}
            for r in range(len(record_dict)):
                new_record_dict[record_dict[r]["CodigoUsuario"]] = record_dict[r]
                    
            if bool(new_record_dict):
                return new_record_dict
            else:
                return None

@app.get("/Usuarios/{CodigoUsuario}")
def get_User_CodigoUsuario(CodigoUsuario: int):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario \
                              , dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password \
                              , dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) as Email, dbo.fn_Descriptografa(Telefone) as Telefone \
                              , dbo.fn_Descriptografa(Celular) as Celular, Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm  \
                           FROM Usuario WITH(NOLOCK) \
                          WHERE CodigoUsuario = ?", CodigoUsuario)

        usuario = cursor.fetchone()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return {
            "CodigoUsuario": usuario.CodigoUsuario,
            "CodigoEmpresa": usuario.CodigoEmpresa,
            "NomeUsuario": usuario.NomeUsuario,
            "Apelido": usuario.Apelido,
            "Password": usuario.Password,
            "CPF": usuario.CPF,
            "Email": usuario.Email,
            "Telefone": usuario.Telefone,
            "Celular": usuario.Celular,
            "Ativo": usuario.Ativo,
            "CodigoGrupoUsuario": usuario.CodigoGrupoUsuario,
            "InseridoPor": usuario.InseridoPor,
            "InseridoEm": usuario.InseridoEm,
            "ModificadoPor": usuario.ModificadoPor,
            "ModificadoEm": usuario.ModificadoEm
        }

@app.post("/Usuarios_post", status_code=HTTPStatus.CREATED)
def create_user(usuario: Usuarios):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
    try:
        cursor = conn.cursor()
        # Convertendo possíveis NaNs para None
        usuario_dict = usuario.dict()
        usuario_dict = {k: (None if pd.isna(v) else v) for k, v in usuario_dict.items()}
        
        cursor.execute("""
            INSERT INTO Usuario (CodigoEmpresa, NomeUsuario, Apelido, Password, CPF, Email, Telefone, Celular, Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, usuario_dict["CodigoEmpresa"], usuario_dict["NomeUsuario"], usuario_dict["Apelido"], usuario_dict["Password"], 
             usuario_dict["CPF"], usuario_dict["Email"], usuario_dict["Telefone"], usuario_dict["Celular"], 
             usuario_dict["Ativo"], usuario_dict["CodigoGrupoUsuario"], usuario_dict["InseridoPor"], 
             usuario_dict["InseridoEm"], usuario_dict["ModificadoPor"], usuario_dict["ModificadoEm"])
        conn.commit()
    except Exception as e:
        print("Erro:", str(e))
        conn.rollback()
        raise HTTPException(status_code=500, detail="Erro ao inserir usuário no banco de dados.")
    finally:
        conn.close()
    
    return {"message": "Usuário criado com sucesso!"}

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
