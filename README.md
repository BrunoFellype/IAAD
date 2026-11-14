# 🤖 Sistema de Gestão - Torneio de Robótica

Sistema web interativo desenvolvido em **Python (Streamlit)** integrado a um banco de dados relacional **MySQL** para gerenciar, auditar e visualizar métricas de equipes, robôs, membros e resultados de um Torneio de Robótica.

O projeto consolida regras de negócio diretamente no motor do banco de dados (via **Triggers**, **Stored Procedures** e **Integridade Referencial**) e apresenta uma interface resiliente com tratamento amigável de exceções e visualização analítica com **Plotly**.

---

## ✨ Funcionalidades e Arquitetura

A aplicação é dividida em três módulos principais na interface web:

### 1. 📊 Dashboard & Consultas Analíticas
* **KPIs em Tempo Real:** Contagem de equipes, total de robôs, provas registradas e média geral de pontuação.
* **Gráficos Interativos (Plotly):** 
  * Gráfico de barras comparando a média de pontuação por equipe e cidade.
  * Gráfico de pizza exibindo a distribuição de provas por categoria de robô.
* **Consulta Não Trivial:** Junção avançada (`LEFT JOIN`) cruzando equipes, robôs e resultados com agrupamento (`GROUP BY`), funções de agregação (`COUNT`, `AVG`, `MAX`, `COALESCE`) e cálculo temporal (`DATEDIFF`) para identificar o tempo de criação do robô mais antigo de cada equipe (incluindo equipes sem robôs cadastrados).

### 2. ⚙️ Gerenciamento Completo (CRUD)
* Operações de **Leitura (Read)**, **Criação (Create)**, **Atualização (Update)** e **Exclusão (Delete)** para todas as entidades (`equipe`, `membro_equipe`, `robo` e `resultado`).
* **Guia de Referência Rápida:** Tabela unificada exibindo os relacionamentos e IDs de equipes, robôs e resultados lado a lado para facilitar o preenchimento de chaves estrangeiras (FK) durante os cadastros.
* **Integração Automática:** O cadastro de novos resultados aciona automaticamente a Stored Procedure de cálculo de classificação.

### 3. 🧪 Regras de Negócio no Banco de Dados (Triggers, Procedures & FK)
Aba dedicada à demonstração e validação das proteções implementadas diretamente no MySQL, com tradução de erros técnicos do SGBD para alertas visuais amigáveis no Streamlit:
* **Trigger `trg_valida_pontuacao_insert`:** Intercepta inserções de resultados e ajusta automaticamente pontuações fora do intervalo permitido (valores `< 0` são zerados para `0.00` e valores `> 100` são limitados a `100.00`).
* **Trigger `trg_valida_compatibilidade_prova`:** Valida a regra de negócio entre a categoria do robô e a modalidade da prova (ex.: *Sumô de Robôs* só compete em *Duelo de Sumô*; *Combate 3kg* apenas em *Arena de Batalha*; *Seguidor de Linha* em *Corrida de Velocidade* ou *Circuito Urbano*), bloqueando inconsistências via `SIGNAL SQLSTATE '45000'`.
* **Stored Procedure `sp_inserir_resultado`:** Insere um novo resultado e recalcula dinamicamente o ranking (`classificacao`) de todos os participantes daquela prova com base na maior pontuação.
* **Stored Procedure `sp_aplicar_bonus_categoria`:** Aplica acréscimos percentuais na pontuação de todos os robôs pertencentes a uma determinada categoria, respeitando o teto máximo de `100.00` pontos.
* **Integridade Referencial (`CASCADE`):** Garante que registros órfãos sejam bloqueados na inserção e que exclusões/atualizações de registros pai propaguem corretamente para as tabelas filhas.

---

## 🗄️ Modelagem do Banco de Dados (`torneio_robotica`)

O banco relacional é composto por 4 tabelas interligadas:
* **`equipe`**: Armazena os dados das equipes participantes (`id_equipe`, `nome_equipe`, `escola`, `cidade`).
* **`membro_equipe`**: Integrantes vinculados a uma equipe (`id_membro`, `nome_membro`, `funcao`, `id_equipe` FK).
* **`robo`**: Robôs inscritos por cada equipe (`id_robo`, `nome_robo`, `categoria`, `data_criacao`, `id_equipe` FK).
* **`resultado`**: Desempenho e ranking dos robôs nas provas (`id_resultado`, `nome_prova`, `classificacao`, `pontuacao`, `id_robo` FK).

---

## 📂 Estrutura do Projeto

```
IAAD/
├── .env.example        # Modelo de variáveis de ambiente
├── .gitignore          # Arquivos e pastas ignorados pelo Git (incluindo .env e venv)
├── README.md           # Documentação completa do projeto
├── requirements.txt    # Dependências Python (Streamlit, MySQL Connector, Pandas, Plotly, Dotenv)
├── app.py              # Código principal da aplicação web e camada de tratamento de erros
└── database/
    └── schema.sql      # Script DDL/DML completo (tabelas, triggers, procedures e povoamento inicial) 
```
---

## ⚙️ Pré-requisitos

Certifique-se de ter instalado na sua máquina:
* **Python** (versão 3.10 ou superior)
* **MySQL Server** (rodando localmente ou em servidor remoto)
* **MySQL Workbench** (opcional, para gerenciamento visual)

---

## 🚀 Passo a Passo para Executar o Projeto

### 1. Clonar o Repositório e Configurar o Ambiente

Clone o projeto para a sua máquina e entre na pasta raiz:
```bash
git clone https://github.com/BrunoFellype/IAAD.git
cd IAAD
```

Crie e ative um ambiente virtual Python:
```bash
# Criar o ambiente virtual
python3 -m venv venv

# Ativar no Linux/macOS
source venv/bin/activate

# Ativar no Windows (PowerShell)
# .\venv\Scripts\Activate
```

Instale as dependências listadas no `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

### 2. Configurar o Banco de Dados MySQL

1. Abra o seu **MySQL Workbench** (ou cliente MySQL de sua preferência).
2. Abra o arquivo localizado em `database/schema.sql` ou copie o seu conteúdo para uma nova aba de SQL.
Execute o script completo de uma só vez. Ele criará o banco torneio_robotica, estruturará as tabelas, compilará as Triggers e Stored Procedures e realizará o povoamento inicial com equipes, membros, robôs e resultados de exemplo.

---

### 3. Configurar as Variáveis de Ambiente (`.env`)

Para proteger dados sensíveis (como a senha do seu banco de dados), a aplicação utiliza variáveis de ambiente.

1. Na raiz do projeto, crie um arquivo chamado **`.env`** (você pode se basear no modelo `.env.example`).
2. Preencha com as suas credenciais locais do MySQL:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=torneio_robotica
DB_PORT=3306
```

---

### 4. Executar a Aplicação (Dashboard)

Com o ambiente virtual ativado e o banco de dados configurado, execute o Streamlit:
```bash
streamlit run app.py
```

O sistema abrirá automaticamente uma aba no seu navegador web padrão no endereço:
👉 `http://localhost:8501`

---

## 👥 Trabalho em Equipe (Colaboradores)
Caso você esteja clonando este repositório pela primeira vez para colaborar com o grupo:
1. Instale as dependências via `pip install -r requirements.txt`.
2. Crie o seu próprio arquivo `.env` localmente (ele não vai para o GitHub por segurança).
3. Execute o script `database/schema.sql` no seu MySQL local para estruturar o banco.
4. Rode o `streamlit run app.py` e comece a desenvolver!