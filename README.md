# 🤖 Sistema de Gestão - Torneio de Robótica

Sistema web para gestão de equipes, robôs e resultados de um torneio de robótica, desenvolvido em **Python**. A aplicação principal utiliza **Streamlit** e **MySQL**; esta branch também apresenta uma implementação **NoSQL com Redis**, incluindo um script de migração dos dados do MySQL.

O projeto permite comparar os modelos relacional e chave-valor: no MySQL, as relações e regras de negócio são definidas no banco; no Redis, os dados são organizados em hashes, sets e sorted sets para consultas por equipe, categoria e ranking.

---

## ✨ Funcionalidades e arquitetura

### 1. Aplicação web com MySQL

O arquivo `app.py` implementa uma interface Streamlit com três áreas:

- **Dashboard e consultas analíticas:** indicadores do torneio, gráficos e consulta agregada de equipes, robôs e resultados.
- **Gerenciamento (CRUD):** leitura, criação, atualização e exclusão de equipes, membros, robôs e resultados.
- **Recursos do banco:** demonstração de triggers, stored procedures e integridade referencial.

A aplicação web continua conectada ao **MySQL**. O código Redis desta branch é um módulo complementar, executado separadamente; não substitui nem altera a conexão usada pelo dashboard.

### 2. Módulo NoSQL com Redis

Os dados do torneio são representados com estas estruturas:

| Estrutura Redis | Padrão de chave | Conteúdo |
|---|---|---|
| Hash | `equipe:{id}` | Nome da equipe e cidade |
| Hash | `robo:{id}` | Nome, categoria e ID da equipe |
| Set | `equipe:{id}:robos` | IDs dos robôs da equipe |
| Set | `categoria:{slug}` | IDs dos robôs da categoria |
| Sorted set | `ranking:{slug_prova}` | Membros `robo:{id}` com pontuação como score |

Os nomes de categorias e provas são normalizados para formar os sufixos das chaves (por exemplo, `Corrida de Velocidade` vira `corrida_de_velocidade`). As consultas no arquivo de carga mostram operações como leitura de hashes, interseção de sets e recuperação de ranking ordenado.

O arquivo `redis/mysql_para_redis.py` copia equipes, robôs e resultados do banco MySQL para o Redis. **A migração limpa o banco Redis selecionado com `FLUSHDB` antes de copiar os dados.** Use uma instância/banco Redis dedicado ou sem dados que você queira preservar.

### 3. Modelo relacional

O script `database/schema.sql` cria o banco `torneio_robotica` e as tabelas `equipe`, `membro_equipe`, `robo` e `resultado`. Também define chaves estrangeiras com cascata, regras para compatibilidade entre categoria e prova, limites de pontuação e procedimentos para inserção e recálculo de ranking.

> **Atenção:** `database/schema.sql` começa com `DROP DATABASE IF EXISTS torneio_robotica`. Executá-lo apaga e recria esse banco. Faça backup se já tiver dados importantes.

---

## 📂 Estrutura do projeto

```text
IAAD/
├── .env.example             # Exemplo de configuração de conexão MySQL
├── README.md                # Documentação geral e instruções de execução
├── app.py                   # Aplicação web Streamlit ligada ao MySQL
├── requirements.txt         # Dependências da aplicação principal
├── database/
│   ├── schema.sql           # Criação/população do banco MySQL e regras de negócio
│   └── torneio_robotica.mwb # Modelo do banco para MySQL Workbench
└── redis/
    ├── README.md            # Notas específicas do módulo Redis
    ├── modelagem_redis.png  # Diagrama da modelagem NoSQL
    ├── mysql_para_redis.py  # Migração de dados do MySQL para o Redis
    ├── requirements.txt     # Dependência Python do módulo Redis
    └── torneio.redis        # Carga de demonstração e consultas/alterações via redis-cli
```

---

## ⚙️ Pré-requisitos

- **Python** 3.10 ou superior.
- **MySQL Server** para usar a aplicação web e/ou migrar dados para Redis.
- **Redis** para executar o módulo NoSQL (pode ser iniciado com Docker, conforme abaixo).
- **Docker** (opcional, recomendado para iniciar o Redis rapidamente).

---

## 🚀 Como executar

### 1. Obter esta branch e configurar o Python

```bash
git clone https://github.com/BrunoFellype/IAAD.git
cd IAAD
git checkout entrega/redis-nosql

python -m venv venv
```

Ative o ambiente virtual:

```bash
# Linux/macOS
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

Instale as dependências da aplicação principal:

```bash
pip install -r requirements.txt
```

### 2. Configurar e criar o banco MySQL

Para a aplicação Streamlit ou a migração MySQL → Redis, configure um MySQL acessível e crie o banco e os dados iniciais:

1. Confira o aviso de remoção de dados acima.
2. Execute `database/schema.sql` em um cliente MySQL, como MySQL Workbench, ou pelo terminal:

```bash
mysql -u root -p < database/schema.sql
```

O comando pressupõe que o cliente `mysql` esteja instalado e que o usuário tenha permissão para criar e remover o banco `torneio_robotica`.

Crie um arquivo `.env` na raiz do projeto com as credenciais do seu MySQL (use `.env.example` como referência):

```dotenv
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=torneio_robotica
DB_PORT=3306
```

### 3. Executar a aplicação web (MySQL)

Com o MySQL em execução, o banco preparado e o ambiente virtual ativo:

```bash
streamlit run app.py
```

A interface estará disponível em `http://localhost:8501`. Essa aplicação usa MySQL, não Redis.

### 4. Iniciar Redis e carregar os dados de demonstração

Inicie uma instância Redis local usando Docker:

```bash
docker run -d --name redis-torneio -p 6379:6379 redis:7
```

Para carregar hashes, sets, rankings e executar as consultas/alterações de exemplo definidas em `redis/torneio.redis`:

```bash
docker exec -i redis-torneio redis-cli < redis/torneio.redis
```

O arquivo inicia com `FLUSHDB`, que apaga todas as chaves do banco Redis selecionado antes de carregar os exemplos. Para abrir o cliente interativo, use:

```bash
docker exec -it redis-torneio redis-cli
```

### 5. Migrar os dados existentes do MySQL para Redis (opcional)

Esta opção exige que o MySQL esteja executando, que `database/schema.sql` já tenha sido aplicado e que o `.env` esteja configurado. No mesmo ambiente virtual, instale a dependência Redis:

```bash
pip install -r redis/requirements.txt
```

O script usa `REDIS_HOST` e `REDIS_PORT` se definidos; os valores padrão são `localhost` e `6379`. Execute:

```bash
python redis/mysql_para_redis.py
```

A migração chama `FLUSHDB` antes de copiar os dados. Portanto, não a execute contra um banco Redis que contenha chaves que devem ser mantidas. Ao concluir, o script informa a quantidade de chaves gravadas.

Para parar e remover o container de demonstração:

```bash
docker stop redis-torneio
docker rm redis-torneio
```

---

## 🔎 MySQL × Redis

| Aspecto | MySQL | Redis nesta branch |
|---|---|---|
| Modelo | Tabelas relacionais, chaves primárias e estrangeiras | Chaves e estruturas de dados em memória |
| Integridade | Regras no banco, incluindo FKs, triggers e procedures | Relacionamentos representados por conjuntos/chaves; validação é responsabilidade da aplicação |
| Ranking | Consulta/recálculo relacional | Sorted set, consultado em ordem por score |
| Junção por equipe/categoria | `JOIN` entre tabelas | Interseção de sets (`SINTER`) |
| Uso no projeto | Interface Streamlit e fonte dos dados da migração | Demonstração NoSQL e armazenamento de cópia dos dados |

---

## 👥 Para colaborar

1. Ative o ambiente virtual e instale `requirements.txt`.
2. Configure seu `.env` local; não compartilhe credenciais.
3. Prepare o MySQL com `database/schema.sql` somente se puder recriar o banco.
4. Para a parte Redis, inicie o Redis e escolha a carga de demonstração ou a migração MySQL → Redis, lembrando que ambas limpam o banco Redis selecionado.
5. Execute `streamlit run app.py` para abrir a aplicação web.
