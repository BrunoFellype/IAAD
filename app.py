import os
import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Torneio de Robótica", page_icon="🤖", layout="wide"
)

st.title("🤖 Dashboard do Torneio de Robótica")
st.write(
    "Painel de controle integrado ao banco de dados MySQL (`torneio_robotica`)."
)


# Função de conexão com o banco de dados usando mysql-connector-python
def get_connection():
  return mysql.connector.connect(
      host=os.getenv("DB_HOST", "localhost"),
      user=os.getenv("DB_USER", "root"),
      password=os.getenv("DB_PASSWORD"),
      database=os.getenv("DB_NAME", "torneio_robotica"),
      port=int(os.getenv("DB_PORT", 3306)),
  )


# Função para carregar os dados das tabelas
@st.cache_data(ttl=300)
def load_data(query):
  conn = get_connection()
  df = pd.read_sql(query, conn)
  conn.close()
  return df


# Consultas SQL para as métricas e tabelas
query_geral = """
    SELECT 
        e.nome_equipe, 
        e.escola, 
        e.cidade, 
        r.nome_robo, 
        r.categoria, 
        res.nome_prova, 
        res.classificacao, 
        res.pontuacao
    FROM equipe e
    JOIN robo r ON e.id_equipe = r.id_equipe
    JOIN resultado res ON r.id_robo = res.id_robo
"""

try:
  df = load_data(query_geral)

  # Métricas Principais (KPIs)
  st.subheader("📊 Indicadores do Torneio")
  col1, col2, col3 = st.columns(3)
  col1.metric("Total de Equipes Participantes", df["nome_equipe"].nunique())
  col2.metric("Total de Robôs inscritos", df["nome_robo"].nunique())
  col3.metric("Média de Pontuação", f"{df['pontuacao'].mean():.2f} pts")

  # Filtro interativo por Categoria
  st.sidebar.header("Filtros")
  categorias = st.sidebar.multiselect(
      "Selecione a Categoria do Robô",
      options=df["categoria"].unique(),
      default=df["categoria"].unique(),
  )

  df_filtered = df[df["categoria"].isin(categorias)]

  # Exibição de Dados Detalhados
  st.subheader("📋 Tabela Geral de Desempenho")
  st.dataframe(df_filtered, use_container_width=True)

  # Gráfico de Pontuação por Robô
  st.subheader("🏆 Pontuação por Robô")
  df_grafico = df_filtered[["nome_robo", "pontuacao"]].set_index("nome_robo")
  st.bar_chart(df_grafico)

  # Seção da Nova Tabela (Membros)
  st.subheader("👥 Membros Cadastrados nas Equipes")
  df_membros = load_data(
      "SELECT m.nome_membro, m.funcao, e.nome_equipe FROM membro_equipe m JOIN"
      " equipe e ON m.id_equipe = e.id_equipe"
  )
  st.dataframe(df_membros, use_container_width=True)

except Exception as e:
  st.error(
      f"Erro ao conectar ou consultar o banco de dados MySQL: {e}. Verifique"
      " suas credenciais de acesso."
  )
