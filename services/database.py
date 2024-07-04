from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Connect to Supabase
DATABASE_URL = 'postgresql+asyncpg://postgres.qbhudqbkuvmjbtxleepf:@P0c@lyPs3@071785@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

# Cria a engine assíncrona do SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Cria a base declarativa para definir modelos de tabelas
Base = declarative_base()

# Função para obter a sessão do banco de dados
async def get_session():
    async with SessionLocal() as session:
        yield session

# Função para inicializar o banco de dados
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)