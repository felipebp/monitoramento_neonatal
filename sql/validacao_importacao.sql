-- ============================================================================
-- AUDITORIA E VALIDAÇÃO DE IMPORTAÇÃO (SINASC, SIM E COORTE ANALÍTICA)
-- Projeto: NeonatoScan — Monitoramento de Risco de Mortalidade Neonatal (CE)
-- ============================================================================

-- 1. INVENTÁRIO DE TABELAS E VOLUMETRIA ESTIMADA (Staging + Analytics)
-- Verifica se todas as tabelas foram criadas e populadas nos schemas esperados.
SELECT
    schemaname AS schema,
    relname AS tabela,
    n_live_tup AS registros_estimados,
    pg_size_pretty(pg_total_relation_size(relid)) AS tamanho_total
FROM pg_stat_user_tables
WHERE schemaname IN ('public', 'analytics')
ORDER BY schemaname, relname;


-- 2. VOLUMETRIA EXATA E TAXA DE MORTALIDADE NEONATAL NA COORTE FINAL
-- Confirma o total de nascidos vivos consolidados (~594 mil) e a proporção de óbitos.
SELECT
    COUNT(*) AS total_nascimentos,
    COUNT(*) FILTER (WHERE obito_neonatal = 0) AS sobreviventes,
    COUNT(*) FILTER (WHERE obito_neonatal = 1) AS obitos_neonatais,
    ROUND(
        (COUNT(*) FILTER (WHERE obito_neonatal = 1)::numeric / NULLIF(COUNT(*), 0)) * 1000,
        2
    ) AS taxa_mortalidade_por_mil
FROM analytics.base_neonatal_pura;


-- 3. AUDITORIA DE INTEGRIDADE E DOMÍNIO CLÍNICO (NULOS E OUTLIERS)
-- Todos os contadores abaixo devem retornar 0 após a execução de linkage_ceara.sql.
SELECT
    COUNT(*) FILTER (WHERE peso IS NULL OR peso <= 0) AS peso_invalido,
    COUNT(*) FILTER (WHERE apgar5 IS NULL OR apgar5 NOT BETWEEN 0 AND 10) AS apgar5_invalido,
    COUNT(*) FILTER (WHERE semana_gestacao IS NULL OR semana_gestacao <= 0) AS gestacao_invalida,
    COUNT(*) FILTER (WHERE idade_mae IS NULL OR idade_mae <= 0) AS idade_mae_invalida,
    COUNT(*) FILTER (WHERE TRIM(sexo) NOT IN ('M', 'F')) AS sexo_invalido,
    COUNT(*) FILTER (WHERE TRIM(id_anomalia) NOT IN ('1', '2')) AS anomalia_invalida
FROM analytics.base_neonatal_pura;


-- 4. SANITY CHECK EPIDEMIOLÓGICO POR DESFECHO (0 = Sobrevivente | 1 = Óbito)
-- Valida a coerência clínica do linkage: espera-se menor peso, Apgar5 e idade
-- gestacional no grupo de óbito neonatal.
SELECT
    obito_neonatal,
    COUNT(*) AS n_registros,
    ROUND(AVG(peso)::numeric, 1) AS media_peso_g,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY peso) AS mediana_peso_g,
    ROUND(AVG(apgar5)::numeric, 2) AS media_apgar5,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY apgar5) AS mediana_apgar5,
    ROUND(AVG(semana_gestacao)::numeric, 1) AS media_semanas_gestacao,
    ROUND(AVG(idade_mae)::numeric, 1) AS media_idade_mae
FROM analytics.base_neonatal_pura
GROUP BY obito_neonatal
ORDER BY obito_neonatal;


-- 5. INSPEÇÃO VISUAL DE AMOSTRA
SELECT *
FROM analytics.base_neonatal_pura
LIMIT 10;
