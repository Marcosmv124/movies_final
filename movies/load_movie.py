import os
import sys
import environ
import requests
import psycopg2
from datetime import datetime, date, timezone


# ---------- ENV ----------
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '..', '.env'))

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {env('API_TOKEN')}"
}


# ---------- DB ----------
def get_connection():
    return psycopg2.connect(
        dbname="dbmovies_final",
        user="django",
        password="master",
        host="localhost",
        port="5432"
    )


# ---------- MAIN LOGIC ----------
def add_movie(movie_id, conn):
    cur = conn.cursor()

    # --- MOVIE ---
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US",
        headers=HEADERS
    )
    m = r.json()

    if "title" not in m:
        print(f"❌ Error TMDB con id {movie_id}")
        return

    cur.execute(
        "SELECT id FROM movies_movie WHERE tmdb_id = %s",
        (movie_id,)
    )
    if cur.fetchone():
        print(f"⏭️  {m['title']} ya existe, saltando")
        return

    # --- CREDITS ---
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US",
        headers=HEADERS
    )
    credits = r.json()

    actors = [(a["name"], a["known_for_department"]) for a in credits["cast"][:10]]
    crew = [(c["name"], c["job"]) for c in credits["crew"][:15]]
    credits_list = actors + crew

    # --- JOBS ---
    jobs = {job for _, job in credits_list}
    cur.execute("SELECT name FROM movies_job WHERE name IN %s", (tuple(jobs),))
    existing_jobs = {row[0] for row in cur.fetchall()}

    cur.executemany(
        "INSERT INTO movies_job (name) VALUES (%s)",
        [(j,) for j in jobs if j not in existing_jobs]
    )

    # --- PERSONS ---
    persons = {person for person, _ in credits_list}
    cur.execute("SELECT name FROM movies_person WHERE name IN %s", (tuple(persons),))
    existing_persons = {row[0] for row in cur.fetchall()}

    cur.executemany(
        "INSERT INTO movies_person (name) VALUES (%s)",
        [(p,) for p in persons if p not in existing_persons]
    )

    # --- GENRES ---
    genres = [g["name"] for g in m["genres"]]
    cur.execute("SELECT name FROM movies_genre WHERE name IN %s", (tuple(genres),))
    existing_genres = {row[0] for row in cur.fetchall()}

    cur.executemany(
        "INSERT INTO movies_genre (name) VALUES (%s)",
        [(g,) for g in genres if g not in existing_genres]
    )

    # --- INSERT MOVIE ---
    release_date = datetime.combine(
        date.fromisoformat(m["release_date"]),
        datetime.min.time(),
        tzinfo=timezone.utc
    )

    cur.execute(
        """
        INSERT INTO movies_movie
        (title, overview, release_date, running_time, budget, tmdb_id, revenue, poster_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            m["title"],
            m["overview"],
            release_date,
            m["runtime"],
            m["budget"],
            movie_id,
            m["revenue"],
            m["poster_path"]
        )
    )

    movie_db_id = cur.fetchone()[0]

    # --- MOVIE ↔ GENRES ---
    cur.execute(
        """
        INSERT INTO movies_movie_genres (movie_id, genre_id)
        SELECT %s, id FROM movies_genre WHERE name IN %s
        """,
        (movie_db_id, tuple(genres))
    )

    # --- CREDITS ---
    for person, job in credits_list:
        cur.execute(
            """
            INSERT INTO movies_moviecredit (movie_id, person_id, job_id)
            VALUES (
                %s,
                (SELECT id FROM movies_person WHERE name = %s),
                (SELECT id FROM movies_job WHERE name = %s)
            )
            """,
            (movie_db_id, person, job)
        )

    conn.commit()
    print(f"✅ Insertada: {m['title']}")


# ---------- ENTRYPOINT ----------
if __name__ == "__main__":
    conn = get_connection()

    for movie_id in sys.argv[1:]:
        try:
            add_movie(int(movie_id), conn)
        except Exception as e:
            conn.rollback()
            print(f"❌ Error con ID {movie_id}: {e}")

    conn.close()
