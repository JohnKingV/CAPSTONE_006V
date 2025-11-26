import psycopg

conn = psycopg.connect("dbname=postgres user=postgres password=pastel123 host=localhost port=5432")
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", ("db_diagnosticadoc",))
    if cur.fetchone():
        print("DB ya existe")
    else:
        cur.execute("CREATE DATABASE db_diagnosticadoc")
        print("DB creada")
conn.close()
