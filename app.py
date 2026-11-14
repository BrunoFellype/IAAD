import os
import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Sistema Torneio de Robótica", page_icon="🤖", layout="wide"
)


# --- FUNÇÕES DE CONEXÃO E EXECUÇÃO ---
def get_connection():
  return mysql.connector.connect(
      host=os.getenv("DB_HOST", "localhost"),
      user=os.getenv("DB_USER", "root"),
      password=os.getenv("DB_PASSWORD"),
      database=os.getenv("DB_NAME", "torneio_robotica"),
      port=int(os.getenv("DB_PORT", 3306)),
  )


def run_query(query, params=None):
  conn = get_connection()
  df = pd.read_sql(query, conn, params=params)
  conn.close()
  return df


def execute_command(query, params=None):
  conn = get_connection()
  cursor = conn.cursor()
  try:
    cursor.execute(query, params or ())
    conn.commit()
    return True, "Operação realizada com sucesso!"
  except mysql.connector.Error as err:
    conn.rollback()
    
    # Captura o texto do erro do MySQL
    err_msg = str(err)
    
    # Erro customizado da Trigger (SIGNAL SQLSTATE '45000' / Código 1644)
    if err.errno == 1644 or "45000" in err_msg:
      if "1644 (" in err_msg:
        partes = err_msg.split("): ")
        msg_limpa = partes[1] if len(partes) > 1 else err.msg
      else:
        msg_limpa = err.msg
      return False, f"🛑 {msg_limpa}"
      
    elif err.errno == 1452:
      return False, "🔗 **Erro de Integridade:** O ID informado (Equipe ou Robô) não existe no banco de dados."
      
    elif err.errno == 1062:
      return False, "⚠️ **Erro de Duplicidade:** Este registro já está cadastrado."
      
    else:
      return False, f"❌ **Erro no Banco de Dados:** {err.msg}"
      
  except Exception as e:
    # Captura qualquer outro erro inesperado do Python sem estourar o traceback na tela
    return False, f"❌ **Erro inesperado:** {str(e)}"
    
  finally:
    cursor.close()
    conn.close()


# --- CABEÇALHO ---
st.title("🤖 Sistema de Gestão - Torneio de Robótica")

aba_dash, aba_crud, aba_avancado = st.tabs([
    "📊 Dashboard & Consultas Analíticas",
    "⚙️ Gerenciamento (CRUD)",
    "🧪 Trigger, Procedure & Integridade (FK)",
])

# ==============================================================================
# ABA 1: DASHBOARD & CONSULTA NÃO TRIVIAL
# ==============================================================================
with aba_dash:
  st.header("Visão Geral do Torneio")

  # Consulta Não Trivial: LEFT JOIN, GROUP BY, Agregações (COUNT, AVG, MAX) e Manipulação de Datas (DATEDIFF)
  query_nao_trivial = """
        SELECT 
            e.nome_equipe AS Equipe,
            e.cidade AS Cidade,
            COUNT(DISTINCT r.id_robo) AS Qtd_Robos,
            COUNT(res.id_resultado) AS Provas_Disputadas,
            COALESCE(ROUND(AVG(res.pontuacao), 2), 0) AS Media_Pontuacao,
            COALESCE(MAX(res.pontuacao), 0) AS Maior_Pontuacao,
            COALESCE(MAX(DATEDIFF(CURDATE(), r.data_criacao)), 0) AS Dias_Robo_Mais_Antigo
        FROM equipe e
        LEFT JOIN robo r ON e.id_equipe = r.id_equipe
        LEFT JOIN resultado res ON r.id_robo = res.id_robo
        GROUP BY e.id_equipe, e.nome_equipe, e.cidade
        ORDER BY Media_Pontuacao DESC;
    """
  df_analitico = run_query(query_nao_trivial)

  # KPIs
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total de Equipes", len(df_analitico))
  col2.metric("Total de Robôs", int(df_analitico["Qtd_Robos"].sum()))
  col3.metric(
      "Provas Registradas", int(df_analitico["Provas_Disputadas"].sum())
  )
  col4.metric(
      "Média Geral",
      f"{df_analitico[df_analitico['Media_Pontuacao'] > 0]['Media_Pontuacao'].mean():.2f} pts",
  )

  st.divider()

  # Gráficos com Plotly
  col_g1, col_g2 = st.columns(2)
  with col_g1:
    fig_bar = px.bar(
        df_analitico,
        x="Equipe",
        y="Media_Pontuacao",
        color="Cidade",
        title="Média de Pontuação por Equipe (incluindo equipes sem provas)",
        text_auto=True,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

  with col_g2:
    df_cat = run_query("""
            SELECT r.categoria AS Categoria, COUNT(res.id_resultado) AS Total_Provas, AVG(res.pontuacao) AS Media
            FROM robo r
            JOIN resultado res ON r.id_robo = res.id_robo
            GROUP BY r.categoria
        """)
    fig_pie = px.pie(
        df_cat,
        names="Categoria",
        values="Total_Provas",
        title="Distribuição de Provas por Categoria de Robô",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  st.subheader(
      "📋 Resultado da Consulta Não Trivial (LEFT JOIN + GROUP BY + Agregação +"
      " Datas)"
  )
  st.caption(
      "Note que equipes sem robôs cadastrados (ex: MechWarriors) aparecem com"
      " valores zerados graças ao LEFT JOIN."
  )
  st.dataframe(df_analitico, use_container_width=True)

# ==============================================================================
# ABA 2: OPERAÇÕES CRUD COMPLETAS + REFERÊNCIA RÁPIDA DE IDS
# ==============================================================================
with aba_crud:
  st.header("Operações CRUD nas Tabelas")
  tabela_escolhida = st.selectbox(
      "Selecione a tabela para gerenciar:",
      ["equipe", "membro_equipe", "robo", "resultado"],
      key="select_tabela_crud"
  )

  # --- READ ---
  st.subheader(f"🔍 Leitura (Read) - Tabela `{tabela_escolhida}`")
  df_tabela = run_query(f"SELECT * FROM {tabela_escolhida}")
  st.dataframe(df_tabela, use_container_width=True)

  col_c, col_u, col_d = st.columns(3)

  # --- CREATE ---
  with col_c:
    st.subheader("➕ Inserir (Create)")
    if tabela_escolhida == "equipe":
      with st.form("form_create_equipe"):
        nome = st.text_input("Nome da Equipe")
        escola = st.text_input("Escola/Instituição")
        cidade = st.text_input("Cidade")
        if st.form_submit_button("Salvar Equipe"):
          ok, msg = execute_command(
              "INSERT INTO equipe (nome_equipe, escola, cidade) VALUES (%s, %s, %s)",
              (nome, escola, cidade),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "membro_equipe":
      with st.form("form_create_membro"):
        nome = st.text_input("Nome do Membro")
        funcao = st.text_input("Função (ex: Programador, Piloto)")
        id_eq = st.number_input("ID da Equipe (FK)", min_value=1, step=1)
        if st.form_submit_button("Salvar Membro"):
          ok, msg = execute_command(
              "INSERT INTO membro_equipe (nome_membro, funcao, id_equipe) VALUES (%s, %s, %s)",
              (nome, funcao, id_eq),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "robo":
      with st.form("form_create_robo"):
        nome = st.text_input("Nome do Robô")
        cat = st.selectbox(
            "Categoria", ["Seguidor de Linha", "Sumô de Robôs", "Combate 3kg"]
        )
        data_c = st.date_input("Data de Criação")
        id_eq = st.number_input("ID da Equipe (FK)", min_value=1, step=1)
        if st.form_submit_button("Salvar Robô"):
          ok, msg = execute_command(
              "INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES (%s, %s, %s, %s)",
              (nome, cat, data_c, id_eq),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "resultado":
      with st.form("form_create_res"):
        PROVAS_OFICIAIS = [
            "Corrida de Velocidade",
            "Duelo de Sumô",
            "Arena de Batalha",
            "Circuito Urbano",
        ]
        prova = st.selectbox("Selecione a Prova Oficial", PROVAS_OFICIAIS)
        pontos = st.number_input(
            "Pontuação (A Trigger ajusta < 0 ou > 100)", value=85.0
        )
        id_rb = st.number_input(
            "ID do Robô Participante (FK)", min_value=1, step=1
        )

        st.caption(
            "ℹ️ A Stored Procedure do banco vai inserir e calcular a classificação automaticamente!"
        )

        if st.form_submit_button("Salvar Resultado"):
          ok, msg = execute_command(
              "CALL sp_inserir_resultado(%s, %s, %s)", (prova, pontos, id_rb)
          )
          if ok:
            st.success("Resultado cadastrado e ranking recalculado com sucesso!")
            st.rerun()
          else:
            st.error(msg)

  # --- UPDATE ---
  with col_u:
    st.subheader("✏️ Atualizar (Update)")
    if tabela_escolhida == "equipe":
      with st.form("form_upd_equipe"):
        id_alvo = st.number_input("ID da Equipe a atualizar", min_value=1, step=1)
        nova_cidade = st.text_input("Nova Cidade")
        if st.form_submit_button("Atualizar Cidade"):
          ok, msg = execute_command(
              "UPDATE equipe SET cidade = %s WHERE id_equipe = %s",
              (nova_cidade, id_alvo),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "membro_equipe":
      with st.form("form_upd_membro"):
        id_alvo = st.number_input("ID do Membro", min_value=1, step=1)
        nova_funcao = st.text_input("Nova Função")
        if st.form_submit_button("Atualizar Função"):
          ok, msg = execute_command(
              "UPDATE membro_equipe SET funcao = %s WHERE id_membro = %s",
              (nova_funcao, id_alvo),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "robo":
      with st.form("form_upd_robo"):
        id_alvo = st.number_input("ID do Robô", min_value=1, step=1)
        novo_nome = st.text_input("Novo Nome do Robô")
        if st.form_submit_button("Atualizar Robô"):
          ok, msg = execute_command(
              "UPDATE robo SET nome_robo = %s WHERE id_robo = %s",
              (novo_nome, id_alvo),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

    elif tabela_escolhida == "resultado":
      with st.form("form_upd_res"):
        id_alvo = st.number_input("ID do Resultado", min_value=1, step=1)
        nova_pont = st.number_input(
            "Nova Pontuação", min_value=0.0, max_value=100.0
        )
        if st.form_submit_button("Atualizar Pontuação"):
          ok, msg = execute_command(
              "UPDATE resultado SET pontuacao = %s WHERE id_resultado = %s",
              (nova_pont, id_alvo),
          )
          if ok:
            st.success(msg)
            st.rerun()
          else:
            st.error(msg)

  # --- DELETE ---
  with col_d:
    st.subheader("🗑️ Excluir (Delete)")
    pk_map = {
        "equipe": "id_equipe",
        "membro_equipe": "id_membro",
        "robo": "id_robo",
        "resultado": "id_resultado",
    }
    pk_col = pk_map[tabela_escolhida]
    with st.form("form_delete"):
      id_del = st.number_input(f"ID ({pk_col}) para excluir", min_value=1, step=1)
      st.caption("⚠️ Excluir registros pai remove as dependências em cascata.")
      if st.form_submit_button("Excluir Registro"):
        ok, msg = execute_command(
            f"DELETE FROM {tabela_escolhida} WHERE {pk_col} = %s", (id_del,)
        )
        if ok:
          st.success(msg)
          st.rerun()
        else:
          st.error(msg)

  # --- PAINEL DE REFERÊNCIA RÁPIDA DE IDS E JUNÇÕES ---
  st.markdown("---")
  st.subheader("🔗 Guia de Referência Rápida (IDs, Equipes e Robôs Vinculados)")
  st.caption("Use esta tabela unificada para consultar rapidamente os IDs.")

  query_referencia = """
        SELECT 
            e.id_equipe AS ID_Eq,
            e.nome_equipe AS Equipe,
            r.id_robo AS ID_Robo,
            r.nome_robo AS Robo,
            res.id_resultado AS ID_Res,
            res.nome_prova AS Prova,
            res.classificacao AS Classif,
            res.pontuacao AS Pontos
        FROM equipe e
        LEFT JOIN robo r ON e.id_equipe = r.id_equipe
        LEFT JOIN resultado res ON r.id_robo = res.id_robo;
    """
  df_ref = run_query(query_referencia)
  st.dataframe(df_ref, use_container_width=True)

# ==============================================================================
# ABA 3: DEMONSTRAÇÃO DE TRIGGERS, STORED PROCEDURE E INTEGRIDADE REFERENCIAL
# ==============================================================================
with aba_avancado:
  st.header("Recursos Avançados e Regras de Negócio do Banco de Dados")
  st.write(
      "Esta seção demonstra os mecanismos implementados diretamente no motor do"
      " MySQL para garantir a inteligência, automação e integridade dos dados."
  )

  col_t1, col_t2 = st.columns(2)

  # --- 1. TESTE DA TRIGGER DE VALIDAÇÃO DE PONTUAÇÃO ---
  with col_t1:
    st.subheader("⚡ Trigger 1: Limite de Pontuação")
    st.write(
        "Intercepta inserções e limita valores menores que 0 (vira 0) ou maiores"
        " que 100 (trava em 100.00)."
    )

    with st.form("form_trg_pontos"):
      id_robo_t1 = st.number_input(
          "ID do Robô", min_value=1, step=1, value=1, key="trg1_robo"
      )
      pontos_t1 = st.number_input(
          "Pontuação Exagerada (ex: 150.0)", value=150.0, key="trg1_pontos"
      )
      if st.form_submit_button("Testar Trigger de Pontuação"):
        ok, msg = execute_command(
            "INSERT INTO resultado (nome_prova, classificacao, pontuacao,"
            " id_robo) VALUES ('Teste Trigger Pontos', 0, %s, %s)",
            (pontos_t1, id_robo_t1),
        )
        if ok:
          st.success(
              "Inserido com sucesso! O banco limitou o valor para 100.00 através"
              " da Trigger."
          )
          st.rerun()
        else:
          st.error(msg)

  # --- 2. TESTE DA TRIGGER DE COMPATIBILIDADE DE CATEGORIA ---
  with col_t2:
    st.subheader("🛑 Trigger 2: Compatibilidade Categoria x Prova")
    st.write(
        "Impede que um robô participe de uma prova incompatível com a sua"
        " categoria (ex: Sumô só em Duelo de Sumô)."
    )

    with st.form("form_trg_compat"):
      id_robo_t2 = st.number_input(
          "ID do Robô (verifique a categoria dele na Aba 2)",
          min_value=1,
          step=1,
          value=1,
          key="trg2_robo",
      )
      prova_incompativel = st.selectbox(
          "Tentar Inscrever na Prova",
          [
              "Duelo de Sumô",
              "Arena de Batalha",
              "Corrida de Velocidade",
              "Circuito Urbano",
          ],
          key="trg2_prova",
      )
      
      if st.form_submit_button("Testar Regra de Compatibilidade"):
        ok, msg = execute_command(
            "CALL sp_inserir_resultado(%s, 80.0, %s)",
            (prova_incompativel, id_robo_t2),
        )
        if ok:
          st.success("Inscrição permitida pelas regras da categoria!")
          st.rerun()
        else:
          st.error(msg)

  st.divider()

  col_p, col_fk = st.columns(2)

  # --- 3. TESTE DA STORED PROCEDURE ---
  with col_p:
    st.subheader("🚀 Stored Procedure: Inserção com Ranking Automático")
    st.write(
        "Insere o resultado e executa um script interno no banco para atualizar"
        " o ranking de todos os robôs daquela prova."
    )

    with st.form("form_sp_avancada"):
      PROVAS_OFICIAIS_SP = [
          "Corrida de Velocidade",
          "Duelo de Sumô",
          "Arena de Batalha",
          "Circuito Urbano",
      ]
      prova_sp = st.selectbox(
          "Escolha a Prova Oficial", PROVAS_OFICIAIS_SP, key="sp_prova"
      )
      pontos_sp = st.number_input("Pontuação do Robô", value=92.5, key="sp_pontos")
      id_robo_sp = st.number_input(
          "ID do Robô Participante", min_value=1, step=1, value=1, key="sp_id_robo"
      )

      if st.form_submit_button("Executar Stored Procedure (`CALL`)"):
        ok, msg = execute_command(
            "CALL sp_inserir_resultado(%s, %s, %s)",
            (prova_sp, pontos_sp, id_robo_sp),
        )
        if ok:
          st.success(
              f"Procedimento executado! Ranking da prova '{prova_sp}'"
              " recalculado."
          )
          st.rerun()
        else:
          st.error(msg)

  # --- 4. TESTE DE INTEGRIDADE REFERENCIAL (FK) ---
  with col_fk:
    st.subheader("🔗 Integridade Referencial (Chave Estrangeira)")
    st.write(
        "Bloqueia a criação de registros órfãos tentando associar elementos a"
        " chaves estrangeiras inexistentes."
    )

    if st.button("Forçar Violação de FK (Equipe 9999)"):
      ok, msg = execute_command(
          "INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe)"
          " VALUES ('Robô Fantasma', 'Sumô de Robôs', '2026-11-14', 9999)"
      )
      if not ok:
        st.error(f"Bloqueio bem-sucedido pelo SGBD!\n\n**Detalhe:** {msg}")
      else:
        st.warning("Inesperado: a inserção passou.")