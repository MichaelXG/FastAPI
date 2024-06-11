import os
import pyodbc
from fastapi import FastAPI, HTTPException
import uvicorn
from models.Usuarios import UpdateUsuarios, Usuarios
from http import HTTPStatus
import pandas as pd
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

@app.get("/UsuariosAll", status_code=HTTPStatus.OK, tags="Usuários")
def get_All_Usuarios():
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
            # Converter o DataFrame em uma lista de dicionários
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
            
@app.get("/Usuarios/{CodigoUsuario}", status_code=HTTPStatus.OK, tags="Usuários")
def get_User_CodigoUsuario(CodigoUsuario: int):
    try:
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
    except Exception as e:
        # Em caso de exceção
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário do banco de dados: {str(e)}")


@app.post("/Usuarios_post", status_code=HTTPStatus.CREATED, tags="Usuários")
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
            VALUES (?, dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), dbo.fn_Criptografa(?), ?, ?, ?, ?, ?, ?)
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


# {
#     "CodigoEmpresa": 1,
#     "NomeUsuario": "Maria",
#     "Apelido": "Maria123",
#     "Password": "senha123",
#     "CPF": "01254785454",
#     "Email": "maria@example.com",
#     "Telefone": "123456789",
#     "Celular": "987654321",
#     "Ativo": true,
#     "CodigoGrupoUsuario": 1,
#     "InseridoPor": 1,
#     "InseridoEm": "2024-06-10T10:00:00",
#     "ModificadoPor": null,
#     "ModificadoEm": null
# }

@app.put("/Usuarios/{CodigoUsuario}", status_code=HTTPStatus.OK, tags="Usuários")
def update_user(CodigoUsuario: int, usuario: UpdateUsuarios):
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
        
        # Convertendo possíveis NaNs para None
        usuario_dict = usuario.dict(exclude_unset=True)
        usuario_dict = {k: (None if pd.isna(v) else v) for k, v in usuario_dict.items()}
        
        # Processamento dos campos a serem criptografados
        encrypt_columns = ["NomeUsuario", "Apelido", "Password", "CPF", "Email", "Telefone", "Celular"]
        for column in encrypt_columns:
            if column in usuario_dict and usuario_dict[column] is not None:
                usuario_dict[column] = f"dbo.fn_Criptografa('{usuario_dict[column]}')"
        
        # Atualiza apenas os campos fornecidos na requisição
        set_clause = ", ".join(f"{key} = {value}" if key in encrypt_columns and value is not None else f"{key} = ?" for key, value in usuario_dict.items())
        params = [value for key, value in usuario_dict.items() if key not in encrypt_columns or value is None]
        params.append(CodigoUsuario)
        
        
        print('set_clause', set_clause)
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

@app.delete("/Usuarios/{CodigoUsuario}", status_code=HTTPStatus.OK, tags="Usuários")
def delete_user(CodigoUsuario: int):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
    
    return {"message": "Usuário deletado com sucesso!"}

# @app.delete("/Usuarios/{CodigoUsuario}")
# def delete_user(CodigoUsuario: int):
#     conn = get_conn()
#     if conn is None:
#         raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")
    
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""SELECT CodigoUsuario FROM Usuario WITH(NOLOCK) WHERE CodigoUsuario = ? """, CodigoUsuario)
#         existing_user = cursor.fetchone()
        
#         if not existing_user:
#             raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
#         cursor.execute("""DELETE FROM Usuario WHERE CodigoUsuario = ? """, CodigoUsuario)
#         conn.commit()
#     except Exception as e:
#         print("Erro:", str(e))
#         conn.rollback()
#         raise HTTPException(status_code=500, detail="Erro ao deletar usuário do banco de dados.")
#     finally:
#         conn.close()

#     return {"message": "Usuário deletado com sucesso!"}