import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def criar_engine():
    url = os.getenv("DATABASE_URL")
    if url:
        return create_engine(url)

    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "datasus_neonatal")

    if not password:
        raise ValueError("Configure DATABASE_URL ou DB_PASSWORD no arquivo '.env'.")

    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")


def auditar_linkage(df: pd.DataFrame) -> None:
    total_pareados = len(df)
    total_obitos = int(df["obito_neonatal"].sum())
    taxa_por_mil = (total_obitos / total_pareados * 1000) if total_pareados > 0 else 0.0

    print("=" * 55)
    print("RELATÓRIO DE AUDITORIA DO LINKAGE (CEARÁ)")
    print("=" * 55)
    print(f"Total de registros pareados : {total_pareados:,}")
    print(f"Quantidade de óbitos (CE)   : {total_obitos:,}")
    print(f"Taxa de mortalidade neonatal: {taxa_por_mil:.2f} por 1.000 NV")
    print("=" * 55)


def main() -> None:
    engine = criar_engine()
    query = "SELECT obito_neonatal FROM analytics.base_neonatal_pura;"
    df = pd.read_sql(query, con=engine)
    auditar_linkage(df)


if __name__ == "__main__":
    main()