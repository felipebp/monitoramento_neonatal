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
    # 1. Métricas da base bruta pareada
    total_bruto = len(df)
    obitos_bruto = int(df["obito_neonatal"].sum())
    taxa_bruta = (obitos_bruto / total_bruto * 1000) if total_bruto > 0 else 0.0

    # 2. Métricas após os filtros clínicos aplicados no modelo
    df_saneado = df[
        df["sexo"].str.strip().isin(["M", "F"])
        & df["id_anomalia"].str.strip().isin(["1", "2"])
        & df["apgar5"].between(0, 10)
        & df["semana_gestacao"].notna()
        & df["peso"].notna()
        & df["idade_mae"].notna()
    ]
    total_saneado = len(df_saneado)
    obitos_saneado = int(df_saneado["obito_neonatal"].sum())
    taxa_saneada = (obitos_saneado / total_saneado * 1000) if total_saneado > 0 else 0.0

    print("=" * 60)
    print("RELATÓRIO DE AUDITORIA DO LINKAGE E SANEAMENTO (CEARÁ)")
    print("=" * 60)
    print(f"[1] Base Bruta Pareada  : {total_bruto:,} NV | {obitos_bruto:,} óbitos ({taxa_bruta:.2f}/1.000)")
    print(f"[2] Coorte Saneada (ML) : {total_saneado:,} NV | {obitos_saneado:,} óbitos ({taxa_saneada:.2f}/1.000)")
    print(f"    Registros excluídos : {total_bruto - total_saneado:,} (campos nulos ou ignorados)")
    print("=" * 60)


def main() -> None:
    engine = criar_engine()
    query = """
        SELECT peso, apgar5, semana_gestacao, idade_mae, id_anomalia, sexo, obito_neonatal
        FROM analytics.base_neonatal_pura;
    """
    df = pd.read_sql(query, con=engine)
    auditar_linkage(df)

if __name__ == "__main__":
    main()