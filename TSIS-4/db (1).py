import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


# подключение к базе
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


# создание таблиц
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_sessions(
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW()
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


# получить или создать игрока
def get_player_id(username):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    row = cur.fetchone()

    if row:
        player_id = row[0]
    else:
        cur.execute(
            "INSERT INTO players(username) VALUES(%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


# сохранить результат
def save_score(username, score, level_reached):
    conn = get_conn()
    cur = conn.cursor()

    player_id = get_player_id(username)

    cur.execute("""
    INSERT INTO game_sessions(player_id, score, level_reached)
    VALUES(%s, %s, %s)
    """, (player_id, int(score), int(level_reached)))

    conn.commit()
    cur.close()
    conn.close()


# лучший score игрока
def get_best(username):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT COALESCE(MAX(g.score), 0)
    FROM game_sessions g
    JOIN players p ON p.id = g.player_id
    WHERE p.username = %s
    """, (username,))

    best = cur.fetchone()[0]

    cur.close()
    conn.close()
    return best


# топ 10 рекордов
def get_top_scores():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT p.username, g.score, g.level_reached, g.played_at
    FROM game_sessions g
    JOIN players p ON p.id = g.player_id
    ORDER BY g.score DESC, g.played_at ASC
    LIMIT 10
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows