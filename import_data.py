from pathlib import Path
import basedosdados as bd

# Configurações de caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
SQL_PATH = BASE_DIR / "sql" / "linkage_ceara.sql"
OUTPUT_DIR = BASE_DIR / r"C:\Users\Felipe Barros\Documents\monitoramento_neonatal"
OUTPUT_FILE = OUTPUT_DIR / "sinasc_sim_ceara.parquet"

PROJECT_ID = "basedosdados-512414"

def carregar_query(caminho_sql: Path) -> str:
    with open(caminho_sql, "r", encoding="utf-8") as f:
        return f.read()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Lendo consulta de: {SQL_PATH}")
    query = carregar_query(SQL_PATH)
    
    print("Enviando requisição ao BigQuery via Base dos Dados...")
    df = bd.read_sql(query, billing_project_id=PROJECT_ID)
    
    print(f"Download concluído: {len(df):,} linhas e {df.shape[1]} colunas.")
    
    df.to_parquet(OUTPUT_FILE, engine="pyarrow", compression="snappy", index=False)
    print(f"Arquivo Parquet salvo com sucesso em:\n-> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()