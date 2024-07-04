
import numpy as np
import pandas as pd

class PadraoDAO(): 
    
    # Função para substituir NaN e NaT por None
    def replace_nan_and_nat_with_none(data):
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, (float, np.floating)) and np.isnan(value):
                cleaned_data[key] = None
            elif isinstance(value, pd.Timestamp) and pd.isna(value):
                cleaned_data[key] = None
            else:
                cleaned_data[key] = value
        return cleaned_data


# Função para obter Usuarios do banco de dados
async def get_items(db: AsyncSession):
    result = await db.execute(select(ItemModel))
    return result.scalars().all()