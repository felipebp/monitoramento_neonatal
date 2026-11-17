import os
from pathlib import Path
import pyarrow.parquet as pq
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_PARQUET = BASE_DIR / "data" / "raw" / "sim_ceara_bruto.parquet"
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


def main() -> None:
    if not ARQUIVO_PARQUET.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_PARQUET}")

    table = pq.read_table(ARQUIVO_PARQUET).replace_schema_metadata(None)
    df = table.to_pandas()

    engine = criar_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS sim;"))

    df.to_sql(
        name="sim_ceara",
        con=engine,
        schema="sim",
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi",
    )
    print(f"Ingestão SIM concluída ({len(df):,} registros em sim.sim_ceara).")


if __name__ == "__main__":
    main()