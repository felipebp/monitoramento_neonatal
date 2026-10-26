from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PARQUET_FILE = BASE_DIR / r"C:\Users\Felipe Barros\Documents\monitoramento_neonatal" / "sinasc_sim_ceara.parquet"

def auditar_linkage(df: pd.DataFrame):
    total = len(df)
    obitos = df['obito_neonatal'].sum()
    tmi = (obitos / total) * 1000
    
    print("=" * 55)
    print("RELATÓRIO DE AUDITORIA DO LINKAGE (CEARÁ 2019-2023)")
    print("=" * 55)
    print(f"Total de registros válidos : {total:,}")
    print(f"Óbitos neonatais pareados  : {obitos:,}")
    print(f"Taxa de Mortalidade Neonatal: {tmi:.2f} por 1.000 nascidos")
    
    # Coerência clínica / biológica
    morte_prematura = df[df['semana_gestacao'] < 28]['obito_neonatal'].mean() * 100
    morte_termo = df[df['semana_gestacao'] >= 37]['obito_neonatal'].mean() * 100
    
    print("\n--- COERÊNCIA BIOLÓGICA ---")
    print(f"Letalidade em prematuros extremos (<28 semanas): {morte_prematura:.2f}%")
    print(f"Letalidade em bebês a termo (>=37 semanas)      : {morte_termo:.2f}%")
    
    # Recorte municipal de Aquiraz
    df_aquiraz = df[df['id_municipio_residencia'] == '2301000']
    obitos_aquiraz = df_aquiraz['obito_neonatal'].sum()
    tmi_aquiraz = (obitos_aquiraz / len(df_aquiraz)) * 1000 if len(df_aquiraz) > 0 else 0
    
    print("\n--- RECORTE MUNICIPAL (AQUIRAZ - IBGE 2301000) ---")
    print(f"Nascimentos em Aquiraz: {len(df_aquiraz):,}")
    print(f"Óbitos em Aquiraz     : {obitos_aquiraz}")
    print(f"Taxa Neonatal Aquiraz : {tmi_aquiraz:.2f} por 1.000")
    print("=" * 55)

def main():
    if not PARQUET_FILE.exists():
        raise FileNotFoundError(f"Arquivo {PARQUET_FILE} não encontrado. Execute o script 01_extracao.py primeiro.")
        
    print(f"Carregando dados locais de: {PARQUET_FILE}")
    df = pd.read_parquet(PARQUET_FILE)
    auditar_linkage(df)

if __name__ == "__main__":
    main()