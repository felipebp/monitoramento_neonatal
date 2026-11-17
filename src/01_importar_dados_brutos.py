import os
import argparse
from pathlib import Path
import basedosdados as bd
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
load_dotenv(BASE_DIR / ".env")

ORIGEM_SINASC = "`basedosdados.br_ms_sinasc.microdados`"
ORIGEM_SIM = "`basedosdados.br_ms_sim.microdados`"


def extrair_sinasc(projeto_gcp: str, forcar: bool = False) -> None:
    arquivo_sinasc = RAW_DIR / "sinasc_ceara_bruto.parquet"

    if arquivo_sinasc.exists() and not forcar:
        print(f"[PULANDO] Arquivo já existe: {arquivo_sinasc}\n")
        return

    print("Extraindo microdados SINASC (Ceará, 2019–2023)...")
    query = f"""
    SELECT
        ano, data_nascimento, id_municipio_residencia, id_municipio_nascimento,
        sexo, peso, apgar1, apgar5, semana_gestacao, id_anomalia,
        tipo_gravidez, tipo_parto, idade_mae, escolaridade_mae, pre_natal
    FROM {ORIGEM_SINASC}
    WHERE sigla_uf = 'CE'
      AND ano BETWEEN 2019 AND 2023
      AND data_nascimento IS NOT NULL
      AND peso IS NOT NULL;
    """
    df = bd.read_sql(query, billing_project_id=projeto_gcp)
    df.to_parquet(arquivo_sinasc, engine="pyarrow", compression="snappy", index=False)
    print(f"-> Concluído ({len(df):,} registros): {arquivo_sinasc}\n")


def extrair_sim(projeto_gcp: str, forcar: bool = False) -> None:
    arquivo_sim = RAW_DIR / "sim_ceara_bruto.parquet"

    if arquivo_sim.exists() and not forcar:
        print(f"[PULANDO] Arquivo já existe: {arquivo_sim}\n")
        return

    print("Extraindo microdados SIM (Ceará, 2019–2024)...")
    query = f"""
    SELECT
        ano, data_nascimento, data_obito, id_municipio_residencia,
        id_municipio_ocorrencia, sexo, peso, idade_mae, causa_basica
    FROM {ORIGEM_SIM}
    WHERE sigla_uf = 'CE'
      AND ano BETWEEN 2019 AND 2024
      AND data_nascimento IS NOT NULL
      AND data_obito IS NOT NULL;
    """
    df = bd.read_sql(query, billing_project_id=projeto_gcp)
    df.to_parquet(arquivo_sim, engine="pyarrow", compression="snappy", index=False)
    print(f"-> Concluído ({len(df):,} registros): {arquivo_sim}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extração SINASC e SIM (Ceará) via Base dos Dados.")
    parser.add_argument("--project-id", default=os.getenv("GCP_PROJECT_ID"), help="ID do projeto GCP.")
    parser.add_argument("--forcar", action="store_true", help="Sobrescreve os arquivos Parquet locais.")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not args.project_id:
        raise ValueError("Defina GCP_PROJECT_ID no arquivo '.env' ou passe '--project-id SEU_ID'.")

    extrair_sinasc(args.project_id, args.forcar)
    extrair_sim(args.project_id, args.forcar)


if __name__ == "__main__":
    main()