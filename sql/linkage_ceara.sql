-- 1. Schema e limpeza
CREATE SCHEMA IF NOT EXISTS analytics;
DROP TABLE IF EXISTS analytics.base_neonatal_pura;

-- 2. Cria a tabela consolidada normalizando o dicionário de sexo (SINASC: 1/2 vs SIM: masculino/feminino)
CREATE TABLE analytics.base_neonatal_pura AS
WITH sim_neonatal AS (
    SELECT DISTINCT
        data_nascimento,
        id_municipio_residencia,
        CASE LOWER(TRIM(sexo))
            WHEN 'masculino' THEN 'M'
            WHEN 'feminino' THEN 'F'
            WHEN '1' THEN 'M'
            WHEN '2' THEN 'F'
            ELSE UPPER(TRIM(sexo))
        END AS sexo_norm,
        peso,
        idade_mae
    FROM sim.sim_ceara
    WHERE data_nascimento IS NOT NULL
      AND data_obito IS NOT NULL
      AND (data_obito::date - data_nascimento::date) BETWEEN 0 AND 27
)
SELECT
    s.peso,
    s.apgar5,
    s.semana_gestacao,
    s.idade_mae,
    CASE TRIM(s.sexo)
        WHEN '1' THEN 'M'
        WHEN '2' THEN 'F'
    END AS sexo,
    TRIM(s.id_anomalia) AS id_anomalia,
    CASE
        WHEN o.data_nascimento IS NOT NULL THEN 1
        ELSE 0
    END AS obito_neonatal
FROM sinasc.sinasc_ceara s
LEFT JOIN sim_neonatal o
    ON s.data_nascimento = o.data_nascimento
   AND s.id_municipio_residencia = o.id_municipio_residencia
   AND (CASE TRIM(s.sexo) WHEN '1' THEN 'M' WHEN '2' THEN 'F' END) = o.sexo_norm
   AND s.peso = o.peso
   AND s.idade_mae = o.idade_mae
WHERE TRIM(s.sexo) IN ('1', '2');