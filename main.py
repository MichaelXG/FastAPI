from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from services.database import Base, get_session, init_db
from models.UsuariosModels import UsuarioModels
from typing import List
      
app = FastAPI(title='API de Usuários', on_startup=[init_db])

# Endpoint para verificar a conexão com o banco de dados
@app.get("/ping", status_code=200, tags=["Verificação"], description="Verificar a conexão com o banco de dados")
async def ping_db(session: AsyncSession = Depends(get_session)):
    try:
        async with session.begin():
            # Executa uma consulta simples para verificar a conexão
            result = await session.execute(text("SELECT 1"))
            return {"message": "Conexão bem-sucedida!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {str(e)}")

# Endpoint para listar todos os usuários
@app.get("/all", status_code=200, tags=["Usuário"], description="Listar todos os Usuários cadastrados")
async def get_usuario_all(session: AsyncSession = Depends(get_session)):
    try:
        async with session.begin():
            comando_sql = text("""
            SELECT CodigoUsuario, CodigoEmpresa, NomeUsuario, Apelido, Password,
                   CPF, Email, Telefone, Celular, Ativo, CodigoGrupoUsuario,
                   InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
            FROM Usuario
            """)
            result = await session.execute(comando_sql)
            records = result.fetchall()

            record_dict_list = [dict(record) for record in records]
            
            return record_dict_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {str(e)}")

# # Endpoint para inserir um novo usuário
# @app.post("/Usuarios", status_code=201, tags=["Usuário"], description="Inserir um novo Usuário", response_model=UsuarioModels)
# async def create_user(usuario: UsuarioModels, session: AsyncSession = Depends(get_session)): 
#     try:
#         async with session.begin():
#             new_user = UsuarioModels(
#                 CodigoEmpresa=usuario.CodigoEmpresa,
#                 NomeUsuario=usuario.NomeUsuario,
#                 Apelido=usuario.Apelido,
#                 Password=usuario.Password,
#                 CPF=usuario.CPF,
#                 Email=usuario.Email,
#                 Telefone=usuario.Telefone,
#                 Celular=usuario.Celular,
#                 Ativo=usuario.Ativo,
#                 CodigoGrupoUsuario=usuario.CodigoGrupoUsuario,
#                 InseridoPor=usuario.InseridoPor,
#                 InseridoEm=usuario.InseridoEm,
#                 ModificadoPor=None,
#                 ModificadoEm=None
#             )
#             session.add(new_user)
#             await session.commit()
            
#             return new_user  # Retornar o usuário criado

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao inserir usuário no banco de dados: {str(e)}")


# # Endpoint para atualizar um usuário
# @app.put("/Usuario/{CodigoUsuario}", status_code=200, tags=["Usuário"], description="Atualizar um Usuário")
# async def update_user(CodigoUsuario: int, usuario: UsuarioModels, session: AsyncSession = Depends(get_session)):
#     try:
#         async with session.begin():
#             comando_sql = text("""
#             SELECT CodigoUsuario, CodigoEmpresa, NomeUsuario, Apelido, Password,
#                    CPF, Email, Telefone, Celular, Ativo, CodigoGrupoUsuario,
#                    InseridoPor, InseridoEm, ModificadoPor, ModificadoEm
#             FROM Usuario
#             WHERE CodigoUsuario = :CodigoUsuario
#             """)
#             result = await session.execute(comando_sql, {"CodigoUsuario": CodigoUsuario})
#             existing_user = result.fetchone()

#             if not existing_user:
#                 raise HTTPException(status_code=404, detail="Usuário não encontrado.")

#             # Atualizar os campos necessários do usuário
#             existing_user = dict(existing_user)
#             existing_user.update(
#                 CodigoEmpresa=usuario.CodigoEmpresa,
#                 NomeUsuario=usuario.NomeUsuario,
#                 Apelido=usuario.Apelido,
#                 Password=usuario.Password,
#                 CPF=usuario.CPF,
#                 Email=usuario.Email,
#                 Telefone=usuario.Telefone,
#                 Celular=usuario.Celular,
#                 Ativo=usuario.Ativo,
#                 CodigoGrupoUsuario=usuario.CodigoGrupoUsuario,
#                 ModificadoPor=usuario.ModificadoPor,
#                 ModificadoEm=datetime.utcnow()
#             )

#             await session.commit()

#             return existing_user

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário no banco de dados: {str(e)}")

# # Endpoint para deletar um usuário
# @app.delete("/Usuario/{ModificadoPor}/{CodigoUsuario}", status_code=200, tags=["Usuário"], description="Deletar um Usuário")
# async def delete_user(ModificadoPor: int, CodigoUsuario: int, session: AsyncSession = Depends(get_session)):
#     try:
#         async with session.begin():
#             comando_sql = text("""
#             SELECT CodigoUsuario
#             FROM Usuario
#             WHERE CodigoUsuario = :CodigoUsuario
#             """)
#             result = await session.execute(comando_sql, {"CodigoUsuario": CodigoUsuario})
#             existing_user = result.fetchone()

#             if not existing_user:
#                 raise HTTPException(status_code=404, detail="Usuário não encontrado.")

#             # Inativar o usuário
#             comando_sql = text("""
#             UPDATE Usuario
#             SET Ativo = False,
#                 ModificadoPor = :ModificadoPor,
#                 ModificadoEm = :ModificadoEm
#             WHERE CodigoUsuario = :CodigoUsuario
#             """)
#             await session.execute(comando_sql, {
#                 "ModificadoPor": ModificadoPor,
#                 "ModificadoEm": datetime.utcnow(),
#                 "CodigoUsuario": CodigoUsuario
#             })

#             await session.commit()

#             return {"message": "Usuário deletado com sucesso!"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário do banco de dados: {str(e)}")

# Rodar o servidor FastAPI com uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)