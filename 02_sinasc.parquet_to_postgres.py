import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine

# 1. Lê a tabela usando o PyArrow diretamente
table = pq.read_table(r"C:\Users\Felipe Barros\Documents\datasets\raw\sinasc_ceara_bruto.parquet")

# 2. Remove os metadados específicos do schema que contêm a referência a 'dbdate'
table = table.replace_schema_metadata(None)

# 3. Converte para Pandas (agora sem erros de compatibilidade)
df = table.to_pandas()

# 4. Ingestão para o PostgreSQL
engine = create_engine('postgresql+psycopg2://casaos:casaos@192.168.4.2:5432/casaos')

df.to_sql(
    name='sinasc_ceara',
    con=engine,
    schema='sinasc',
    if_exists='replace',
    index=False,
    chunksize=10000,
    method='multi'
)

print("Ingestão concluída com sucesso!")