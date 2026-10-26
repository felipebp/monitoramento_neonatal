WITH obitos_neonatais_unicos AS (
    SELECT DISTINCT
        data_nascimento,
        TRIM(id_municipio_residencia) AS id_municipio_residencia,
        UPPER(TRIM(sexo)) AS sexo,
        SAFE_CAST(idade_mae AS INT64) AS idade_mae,
        SAFE_CAST(peso AS INT64) AS peso
    FROM
        `basedosdados.br_ms_sim.microdados`
    WHERE
        sigla_uf = 'CE'
        AND ano BETWEEN 2019 AND 2024
        AND data_nascimento IS NOT NULL
        AND data_obito IS NOT NULL
        AND DATE_DIFF(data_obito, data_nascimento, DAY) BETWEEN 0 AND 27
        AND SAFE_CAST(peso AS INT64) BETWEEN 300 AND 6500
        AND SAFE_CAST(idade_mae AS INT64) BETWEEN 10 AND 60
        AND TRIM(id_municipio_residencia) IS NOT NULL
        AND sexo IN ('M', 'F', '1', '2')
),

nascidos_ceara AS (
    SELECT
        ano,
        data_nascimento,
        TRIM(id_municipio_residencia) AS id_municipio_residencia,
        TRIM(id_municipio_nascimento) AS id_municipio_nascimento,
        UPPER(TRIM(sexo)) AS sexo,
        SAFE_CAST(idade_mae AS INT64) AS idade_mae,
        SAFE_CAST(peso AS INT64) AS peso,
        SAFE_CAST(apgar1 AS INT64) AS apgar1,
        SAFE_CAST(apgar5 AS INT64) AS apgar5,
        SAFE_CAST(semana_gestacao AS INT64) AS semana_gestacao,
        id_anomalia,
        tipo_gravidez,
        tipo_parto
    FROM
        `basedosdados.br_ms_sinasc.microdados`
    WHERE
        sigla_uf = 'CE'
        AND ano BETWEEN 2019 AND 2023
        AND data_nascimento IS NOT NULL
        AND SAFE_CAST(peso AS INT64) BETWEEN 300 AND 6500
        AND SAFE_CAST(idade_mae AS INT64) BETWEEN 10 AND 60
        AND TRIM(id_municipio_residencia) IS NOT NULL
)

SELECT
    nasc.ano,
    nasc.id_municipio_residencia,
    nasc.id_municipio_nascimento,
    nasc.peso,
    nasc.apgar1,
    nasc.apgar5,
    nasc.semana_gestacao,
    nasc.id_anomalia,
    nasc.sexo,
    nasc.tipo_gravidez,
    nasc.tipo_parto,
    CASE 
        WHEN obito.data_nascimento IS NOT NULL THEN 1 
        ELSE 0 
    END AS obito_neonatal
FROM
    nascidos_ceara AS nasc
LEFT JOIN obitos_neonatais_unicos AS obito
    ON  nasc.data_nascimento = obito.data_nascimento
    AND nasc.id_municipio_residencia = obito.id_municipio_residencia
    AND nasc.sexo = obito.sexo
    AND nasc.idade_mae = obito.idade_mae
    AND nasc.peso = obito.peso;