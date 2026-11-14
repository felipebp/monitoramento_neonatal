import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
from sqlalchemy import create_engine
from statsmodels.regression.rolling import weight_parameters

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Monitoramento de Risco Neonatal - UFMS / Ceará",
    page_icon="👶🏽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
    <style>
    .main-header { font-size: 3.2rem !important; color: #f66151; font-weight: 700; margin-bottom: 0px; }
    .sub-header { font-size: 1.2rem !important; color: #4B5563; margin-bottom: 20px; }
    .card-baixo { background-color: #D1FAE5; border-left: 6px solid #10B981; padding: 15px; border-radius: 8px; color: #065F46; }
    .card-medio { background-color: #FEF3C7; border-left: 6px solid #F59E0B; padding: 15px; border-radius: 8px; color: #92400E; }
    .card-alto { background-color: #FEE2E2; border-left: 6px solid #EF4444; padding: 15px; border-radius: 8px; color: #991B1B; }
    .card-baixo h3, .card-medio h3, .card-alto h3 { margin-top: 0px !important; margin-bottom: 10px !important; font-size: 1.35rem !important; color: inherit !important; }
    .card-baixo p, .card-medio p, .card-alto p { margin-bottom: 8px !important; font-size: 1rem !important; }
    .card-baixo ul, .card-medio ul, .card-alto ul { margin-bottom: 0px !important; padding-left: 22px !important; }
    [data-testid="stTabs"] [role="tab"], [data-testid="stTabs"] [role="tab"] * { font-size: 1.0rem !important; font-weight: 700 !important; }
    [data-testid="stTabs"] [role="tab"] { padding: 12px 24px !important; height: auto !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CARREGAMENTO DO MODELO (.PKL) E DA BASE (POSTGRESQL NO ZIMAOS)
# -----------------------------------------------------------------------------
@st.cache_resource
def carregar_modelo_preditivo():
    artefato = joblib.load('modelo_neonatal.pkl')
    return artefato['modelo'], artefato['p80'], artefato['p95'], artefato['colunas']
@st.cache_data

def carregar_dados_coorte():
    # Conecta diretamente no banco de dados hospedado no ZimaOS
    db_url = "postgresql+psycopg2://casaos:casaos@192.168.4.2:5432/casaos"
    engine = create_engine(db_url)
    query = "SELECT peso, apgar5, semana_gestacao, idade_mae, sexo, obito_neonatal FROM analytics.base_neonatal_pura;"
    return pd.read_sql(query, con=engine)

# Executa as funções em cache
modelo, p80_cut, p95_cut, colunas_esperadas = carregar_modelo_preditivo()
df_coorte = carregar_dados_coorte()

# -----------------------------------------------------------------------------
# CABEÇALHO DO DASHBOARD
# -----------------------------------------------------------------------------
st.markdown('<p class="main-header">👶 Monitoramento do Risco de Vida Neonatal</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header" </p>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL: INPUT DE NOVOS DADOS PARA PREDIÇÃO
# -----------------------------------------------------------------------------
st.sidebar.header("📋 Dados do Recém-Nascido")
st.sidebar.markdown("Insira os parâmetros clínicos (DNV ou avaliação leito):")

input_peso = st.sidebar.number_input("Peso ao Nascer (gramas)", min_value=400, max_value=5500, value=3100, step=50)
input_apgar5 = st.sidebar.slider("Escore de Apgar (5º Minuto)", min_value=0, max_value=10, value=9)
input_semana = st.sidebar.number_input("Semanas de Gestação", min_value=20, max_value=42, value=39, step=1)
input_idade_mae = st.sidebar.number_input("Idade da Mãe (anos)", min_value=12, max_value=55, value=25, step=1)
input_sexo = st.sidebar.selectbox("Sexo do Recém-Nascido", options=["Masculino", "Feminino"])

# -----------------------------------------------------------------------------
# MOTOR PREDITIVO: MONTAGEM DO PACIENTE E CÁLCULO DO RISCO
# -----------------------------------------------------------------------------
novo_paciente = pd.DataFrame([{
    'peso': input_peso,
    'apgar5': input_apgar5,
    'semana_gestacao': input_semana,
    'idade_mae': input_idade_mae,
    'sexo_IGN': False,
    'sexo_M': True if input_sexo == "Masculino" else False
}])[colunas_esperadas]

prob_individual = modelo.predict_proba(novo_paciente)[0, 1]

if prob_individual < p80_cut:
    categoria_risco = "Baixo Risco"
    cor_categoria = "#10B981"
    classe_card = "card-baixo"
    recomendacao = """
        <p><strong>Conduta Recomendada (Atenção Primária):</strong></p>
        <ul>
            <li>Acompanhamento puerperal padrão de rotina.</li>
            <li>Agendamento da 1ª consulta de puericultura na UBS em até 15 dias.</li>
            <li>Orientação regular sobre aleitamento e calendário vacinal.</li>
        </ul>
    """
elif prob_individual < p95_cut:
    categoria_risco = "Médio Risco"
    cor_categoria = "#F59E0B"
    classe_card = "card-medio"
    recomendacao = """
        <p><strong>Conduta Recomendada (Vigilância Intensificada):</strong></p>
        <ul>
            <li>Visita domiciliar de enfermagem <strong>obrigatória</strong> na 1ª semana de vida.</li>
            <li>Antecipar 1ª consulta médica na UBS para no máximo 7 dias após a alta.</li>
            <li>Monitoramento prioritário do ganho ponderal e avaliação de icterícia.</li>
        </ul>
    """
else:
    categoria_risco = "Alto Risco"
    cor_categoria = "#EF4444"
    classe_card = "card-alto"
    recomendacao = """
        <p><strong>Conduta Recomendada (Prioridade Absoluta):</strong></p>
        <ul>
            <li>Avaliação pediátrica imediata; verificar indicação clínica para internação/UTI.</li>
            <li>Acionar protocolo de busca ativa e articulação direta com a maternidade.</li>
            <li>Acompanhamento contínuo e rigoroso pela equipe de Saúde da Família.</li>
        </ul>
    """

st.markdown(f"""
    <div class="{classe_card}">
        <h3>Diretriz Clínica - {categoria_risco}</h3>
        {recomendacao}
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTRUTURA VISUAL: ABAS DO DASHBOARD
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["🎯 Diagnóstico Individual", "📊 Perfil Epidemiológico da Coorte", "📈 Transparência do Algoritmo (Odds Ratio)"])

# --- ABA 1: RESULTADO DA TRIAGEM DO PACIENTE ---
with tab1:
    st.subheader("Resultado do Simulador de Triagem")
    col_pred1, col_pred2 = st.columns([1, 1.5])

    with col_pred1:
        st.metric(label="Probabilidade Estatística de Risco", value=f"{prob_individual * 100:.2f}%")
        st.markdown(f"### Classificação: <span style='color:{cor_categoria};'>{categoria_risco}</span>",
                    unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_individual * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Índice Preditivo (%)", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': cor_categoria},
                'steps': [
                    {'range': [0, p80_cut * 100], 'color': "#D1FAE5"},
                    {'range': [p80_cut * 100, p95_cut * 100], 'color': "#FEF3C7"},
                    {'range': [p95_cut * 100, 100], 'color': "#FEE2E2"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.75,
                    'value': prob_individual * 100
                }
            }
        ))
        fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col_pred2:
        st.markdown(f"""
            <div class="{classe_card}">
                <h3>Diretriz Clínica - {categoria_risco}</h3>
                {recomendacao}
            </div>
        """, unsafe_allow_html=True)

# --- ABA 2: GRÁFICOS DA COORTE (VIA POSTGRESQL ZIMAOS) ---
with tab2:
    st.subheader("Indicadores Monitorados (Ceará 2019 - 2024)")

    total_nascimentos = len(df_coorte)
    total_obitos = df_coorte['obito_neonatal'].sum()
    taxa_mortalidade = (total_obitos / total_nascimentos) * 1000

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total de Nascimentos (Base)", f"{total_nascimentos:,}".replace(',', '.'))
    kpi2.metric("Óbitos Pareados", f"{total_obitos:,}".replace(',', '.'))
    kpi3.metric("Taxa de Mortalidade", f"{taxa_mortalidade:.2f} / 1.000")
    kpi4.metric("Estrato de Alto Risco", "Top 5,00 %")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        df_coorte['faixa_peso'] = pd.cut(df_coorte['peso'], bins=[0, 1000, 1500, 2500, 4000, 6000],
                                         labels=['< 1000g', '1000-1499g', '1500-2499g', '2500-3999g', '>= 4000g'])
        taxa_peso = df_coorte.groupby('faixa_peso', observed=False)['obito_neonatal'].mean() * 100
        fig_peso = px.bar(x=taxa_peso.index, y=taxa_peso.values, title="Mortalidade Neonatal por Faixa de Peso (%)",
                          labels={'x': 'Faixa de Peso', 'y': 'Taxa de Óbito (%)'}, color_discrete_sequence=['#1E3A8A'])
        st.plotly_chart(fig_peso, use_container_width=True)

    with col_chart2:
        # 1. Filtra mantendo apenas notas válidas de Apgar (0 a 10), ignorando o código 99 do SUS
        df_apgar_valido = df_coorte[(df_coorte['apgar5'] >= 0) & (df_coorte['apgar5'] <= 10)]

        # 2. Agrupa e calcula a taxa de letalidade (%)
        taxa_apgar = df_apgar_valido.groupby('apgar5', observed=False)['obito_neonatal'].mean() * 100

        # 3. Cria o gráfico de linha
        fig_apgar = px.line(
            x=taxa_apgar.index,
            y=taxa_apgar.values,
            title="Curva de Letalidade por Apgar (5º Minuto)",
            labels={'x': 'Nota Apgar 5', 'y': 'Taxa de Óbito (%)'},
            markers=True,
            color_discrete_sequence=['#EF4444']
        )

        # 4. Força o eixo X a exibir todas as notas numéricas de 0 a 10 (de 1 em 1)
        fig_apgar.update_xaxes(dtick=1, range=[-0.3, 10.3])

        st.plotly_chart(fig_apgar, use_container_width=True)

# --- ABA 3: EXPLICABILIDADE CLÍNICA (ODDS RATIO) ---
with tab3:
    st.subheader("Pesos do Modelo Preditivo (Explicabilidade para a Bancada Médica)")
    st.markdown(
        "A Odds Ratio (Razão de Chances) demonstra o fator multiplicador do risco de vida atrelado a cada variável inserida.")

    coefs = modelo.coef_[0]
    odds = np.exp(coefs)

    df_or = pd.DataFrame(
        {'Atributo Clínico': colunas_esperadas, 'Coeficiente (Beta)': coefs, 'Odds Ratio (e^Beta)': odds}).sort_values(
        by='Odds Ratio (e^Beta)', ascending=False)

    col_or1, col_or2 = st.columns([1, 1.2])
    with col_or1:
        st.dataframe(df_or.style.format({'Coeficiente (Beta)': '{:.4f}', 'Odds Ratio (e^Beta)': '{:.4f}'}),
                     use_container_width=True)
    with col_or2:
        fig_or = px.bar(df_or, x='Odds Ratio (e^Beta)', y='Atributo Clínico', orientation='h',
                        title="Impacto e Fator de Risco por Variável (Odds Ratio)", color='Odds Ratio (e^Beta)',
                        color_continuous_scale='Reds')
        st.plotly_chart(fig_or, use_container_width=True)