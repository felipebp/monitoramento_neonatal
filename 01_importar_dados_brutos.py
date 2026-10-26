from pathlib import Path
import basedosdados as bd

# ==============================================================================
# 1. CONFIGURAÇÃO EXPLÍCITA DE ORIGEM E DESTINO DOS DADOS
# ==============================================================================

# Projeto GCP pessoal (apenas para autenticação e cota gratuita da API)
PROJETO_FATURAMENTO = "basedosdados-512414"

# Repositório de Origem no Google Cloud (Onde o BigQuery busca os dados públicos)
PROJETO_ORIGEM = "basedosdados"

# Mapeamento do Dataset e Tabela do SINASC (Nascidos Vivos)
DATASET_SINASC = "br_ms_sinasc"
TABELA_SINASC = "microdados"
ORIGEM_COMPLETA_SINASC = f"`{PROJETO_ORIGEM}.{DATASET_SINASC}.{TABELA_SINASC}`"

# Mapeamento do Dataset e Tabela do SIM (Mortalidade)
DATASET_SIM = "br_ms_sim"
TABELA_SIM = "microdados"
ORIGEM_COMPLETA_SIM = f"`{PROJETO_ORIGEM}.{DATASET_SIM}.{TABELA_SIM}`"

# Diretórios Locais de Armazenamento
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "dataset" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

ARQUIVO_SINASC = RAW_DIR / "sinasc_ceara_bruto.parquet"
ARQUIVO_SIM = RAW_DIR / "sim_ceara_bruto.parquet"

# ==============================================================================
# 2. FUNÇÕES DE EXTRAÇÃO POR BASE
# ==============================================================================

def extrair_sinasc():
    """Consulta e extrai os microdados de nascimentos diretamente do SINASC."""
    print("=" * 70)
    print(f"EXTRAINDO SINASC")
    print(f"Origem configurada : {ORIGEM_COMPLETA_SINASC}")
    print(f"Faturamento via    : {PROJETO_FATURAMENTO}")
    print("=" * 70)

    query_sinasc = f"""
    SELECT
        ano,
        data_nascimento,
        id_municipio_residencia,
        id_municipio_nascimento,
        sexo,
        peso,
        apgar1,
        apgar5,
        semana_gestacao,
        id_anomalia,
        tipo_gravidez,
        tipo_parto,
        idade_mae,
        escolaridade_mae,
        pre_natal
    FROM
        {ORIGEM_COMPLETA_SINASC}
    WHERE
        sigla_uf = 'CE'
        AND ano BETWEEN 2019 AND 2023
        AND data_nascimento IS NOT NULL
        AND peso IS NOT NULL;
    """

    df_sinasc = bd.read_sql(query_sinasc, billing_project_id=PROJETO_FATURAMENTO)
    print(f"-> Concluído: {len(df_sinasc):,} registros baixados do SINASC.")

    df_sinasc.to_parquet(ARQUIVO_SINASC, engine="pyarrow", compression="snappy", index=False)
    print(f"-> Base gravada em: {ARQUIVO_SINASC}\n")


def extrair_sim():
    """Consulta e extrai os microdados de mortalidade diretamente do SIM."""
    print("=" * 70)
    print(f"EXTRAINDO SIM")
    print(f"Origem configurada : {ORIGEM_COMPLETA_SIM}")
    print(f"Faturamento via    : {PROJETO_FATURAMENTO}")
    print("=" * 70)

    query_sim = f"""
    SELECT
        ano,
        data_nascimento,
        data_obito,
        id_municipio_residencia,
        id_municipio_ocorrencia,
        sexo,
        peso,
        idade_mae,
        causa_basica
    FROM
        {ORIGEM_COMPLETA_SIM}
    WHERE
        sigla_uf = 'CE'
        AND ano BETWEEN 2019 AND 2024
        AND data_nascimento IS NOT NULL
        AND data_obito IS NOT NULL;
    """

    df_sim = bd.read_sql(query_sim, billing_project_id=PROJETO_FATURAMENTO)
    print(f"-> Concluído: {len(df_sim):,} registros baixados do SIM.")

    df_sim.to_parquet(ARQUIVO_SIM, engine="pyarrow", compression="snappy", index=False)
    print(f"-> Base gravada em: {ARQUIVO_SIM}\n")


def main():
    extrair_sinasc()
    extrair_sim()
    print("Pipeline de ingestão bruta finalizado com sucesso.")


if __name__ == "__main__":
    main()