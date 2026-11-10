# 🤖 Dashboard do Torneio de Robótica

Sistema web interativo desenvolvido em **Python (Streamlit)** integrado a um banco de dados relacional **MySQL** para gerenciar e visualizar métricas de equipes, robôs, membros e resultados de um Torneio de Robótica.

---

## 📂 Estrutura do Projeto

```text
IAAD/
├── .env.example        # Modelo de variáveis de ambiente
├── .gitignore          # Arquivos e pastas ignorados pelo Git
├── README.md           # Documentação do projeto
├── requirements.txt    # Lista de dependências Python
├── app.py              # Código principal da aplicação (Streamlit)
└── database/
    └── schema.sql      # Script de criação do banco de dados e tabelas
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
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
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
3. Execute o script completo para criar o banco de dados `torneio_robotica`, as tabelas (`equipe`, `membro_equipe`, `robo`, `resultado`) e os registros iniciais de exemplo.

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