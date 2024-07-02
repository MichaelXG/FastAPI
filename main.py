import os
import pyodbc
from fastapi import FastAPI, HTTPException
import uvicorn
from models.Usuarios import Usuarios
from http import HTTPStatus
import pandas as pd
import numpy as np
from Controllers.PadraoController import *

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

@app.get("/all", status_code=HTTPStatus.OK, tags=["Usuário"], description=" Listar todos os Usuários cadastrados", name="Lista todos os Usuários")
def get_usuario_all():
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados 02.")
    
    with conn:
        cursor = conn.cursor()
      
        try:
            comando_sql = """
            SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario,
                   dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password,
                   dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) as Email,
                   dbo.fn_Descriptografa(Telefone) as Telefone, dbo.fn_Descriptografa(Celular) as Celular,
                   Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
            FROM Usuario WITH(NOLOCK)
            """
            colunas_datas = ['InseridoEm', 'ModificadoEm']
            record = pd.read_sql(comando_sql, conn, parse_dates=colunas_datas)
            record = record.where(pd.notnull(record), None)
            record_dict_list = record.to_dict(orient='records')
         
        except Exception as e:
            print("Erro:", str(e))
            cursor.close()
            raise HTTPException(status_code=500, detail="Erro ao consultar o banco de dados.")
        else:
            new_record_dict_list = []
            for record_dict in record_dict_list:
                new_record_dict = {}
                for key, value in record_dict.items():
                    if isinstance(value, (float, np.floating)) and np.isnan(value):
                        new_record_dict[key] = None
                    elif isinstance(value, pd.Timestamp) and pd.isna(value):
                        new_record_dict[key] = None
                    else:
                        new_record_dict[key] = value
                new_record_dict_list.append(new_record_dict)
                    
            if bool(new_record_dict_list):
                return new_record_dict_list
            else:
                return None
            
@app.get("/Usuario/{CodigoUsuario}", status_code=HTTPStatus.OK, tags=["Usuário"], description="Listar todos os Usuários cadastrados pelo CodigoUsuario", name="Lista todos os usuários pelo CodigoUsuario")
def get_usuario_Codigo_Usuario(CodigoUsuario: int) -> dict:
    try:
        conn = get_conn()
        if conn is None:
            raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
        
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario,
                   dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password,
                   dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) as Email,
                   dbo.fn_Descriptografa(Telefone) as Telefone, dbo.fn_Descriptografa(Celular) as Celular,
                   Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
            FROM Usuario WITH(NOLOCK)
            WHERE CodigoUsuario = ?
            """, CodigoUsuario)

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário do banco de dados: {str(e)}")

@app.post("/Usuarios", status_code=HTTPStatus.CREATED,  tags=["Usuário"], description="inserir um novo Usuários", name="INSERT Usuários")
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

@app.put("/Usuario/{CodigoUsuario}", status_code=HTTPStatus.OK, tags=["Usuário"], description="Alterar um Usuários cadastrados", name="UPDATE Usuários")
def usuario_put(CodigoUsuario: int, usuario: Usuarios) :
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario,
                   dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password,
                   dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) AS Email,
                   dbo.fn_Descriptografa(Telefone) AS Telefone, dbo.fn_Descriptografa(Celular) AS Celular,
                   Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
            FROM Usuario WITH(NOLOCK)
            WHERE CodigoUsuario = ?
        """, CodigoUsuario)
        existing_user = cursor.fetchone()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
        usuario_dict = usuario.dict(exclude_unset=True)
        
        encrypt_columns = ["NomeUsuario", "Apelido", "Password", "CPF", "Email", "Telefone", "Celular"]
        set_clauses = []
        params = []
        
        current_user = {
            "CodigoEmpresa": existing_user.CodigoEmpresa,
            "NomeUsuario": existing_user.NomeUsuario,
            "Apelido": existing_user.Apelido,
            "Password": existing_user.Password,
            "CPF": existing_user.CPF,
            "Email": existing_user.Email,
            "Telefone": existing_user.Telefone,
            "Celular": existing_user.Celular,
            "Ativo": existing_user.Ativo,
            "CodigoGrupoUsuario": existing_user.CodigoGrupoUsuario,
            "ModificadoPor": existing_user.ModificadoPor,
            "ModificadoEm": existing_user.ModificadoEm
        }
        
        for key, value in usuario_dict.items():
            if key in encrypt_columns:
                decrypted_value = current_user[key]
                if decrypted_value != value:
                    set_clauses.append(f"{key} = dbo.fn_Criptografa(?)")
                    params.append(value)
            else:
                if current_user[key] != value:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

        if not set_clauses:
            raise HTTPException(status_code=400, detail="Nenhum campo válido fornecido para atualização.")
        
        set_clause = ", ".join(set_clauses)
        params.append(CodigoUsuario)
        
        cursor.execute(f"""
            UPDATE Usuario
            SET {set_clause}
            WHERE CodigoUsuario = ?
        """, params)
        
        conn.commit()

        cursor.execute("""
            SELECT CodigoUsuario, CodigoEmpresa, dbo.fn_Descriptografa(NomeUsuario) AS NomeUsuario,
                   dbo.fn_Descriptografa(Apelido) AS Apelido, dbo.fn_Descriptografa(Password) AS Password,
                   dbo.fn_Descriptografa(CPF) AS CPF, dbo.fn_Descriptografa(Email) AS Email,
                   dbo.fn_Descriptografa(Telefone) AS Telefone, dbo.fn_Descriptografa(Celular) AS Celular,
                   Ativo, CodigoGrupoUsuario, InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
            FROM Usuario WITH(NOLOCK)
            WHERE CodigoUsuario = ?
        """, CodigoUsuario)
        updated_user = cursor.fetchone()
        
    except Exception as e:
        print("Erro:", str(e))
        conn.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar usuário no banco de dados.")
    finally:
        conn.close()

    return updated_user

@app.delete("/Usuario/{ModificadoPor}/{CodigoUsuario}", status_code=HTTPStatus.OK, tags=["Usuário"], description="Inativar um Usuários cadastrados", name="DELETE Usuários")
def usuario_delete(ModificadoPor:int, CodigoUsuario: int):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT CodigoUsuario FROM Usuario WHERE CodigoUsuario = ?", CodigoUsuario)
        existing_user = cursor.fetchone()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
        cursor.execute("UPDATE Usuario SET Ativo = 0, ModificadoPor = ?, ModificadoEm = GETDATE() WHERE CodigoUsuario = ?", ModificadoPor, CodigoUsuario)
        conn.commit()
    except Exception as e:
        print("Erro:", str(e))
        conn.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar usuário do banco de dados.")
    finally:
        conn.close()

    return {"message": "Usuário deletado com sucesso!"}

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)