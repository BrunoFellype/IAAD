"""Copia os dados do MySQL (torneio_robotica) para o Redis.

Uso: python redis/mysql_para_redis.py
Lê as variáveis DB_* do .env e REDIS_HOST/REDIS_PORT (padrão localhost:6379).
"""
import os
import re
import unicodedata

import mysql.connector
import redis
from dotenv import load_dotenv

load_dotenv()


def slug(texto):
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def migrar(cur, r):
    r.flushdb()
    cur.execute("SELECT id_equipe, nome_equipe, cidade FROM equipe")
    for i, nome, cidade in cur.fetchall():
        r.hset(f"equipe:{i}", mapping={"nome": nome, "cidade": cidade or ""})

    cur.execute("SELECT id_robo, nome_robo, categoria, id_equipe FROM robo")
    for i, nome, cat, eq in cur.fetchall():
        r.hset(f"robo:{i}", mapping={"nome": nome, "categoria": cat, "equipe_id": eq})
        r.sadd(f"equipe:{eq}:robos", i)
        r.sadd(f"categoria:{slug(cat)}", i)

    cur.execute("SELECT nome_prova, pontuacao, id_robo FROM resultado")
    for prova, pts, robo in cur.fetchall():
        r.zadd(f"ranking:{slug(prova)}", {f"robo:{robo}": float(pts)})


def main():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "torneio_robotica"),
        port=int(os.getenv("DB_PORT", "3306")),
    )
    r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")), decode_responses=True)
    migrar(conn.cursor(), r)
    conn.close()
    print("Migração concluída:", r.dbsize(), "chaves no Redis.")


if __name__ == "__main__":
    main()
