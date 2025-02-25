import psycopg2
from psycopg2 import sql

def create_database(dbname, user, password, host="localhost", port="5432"):
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        connection.autocommit = True

        cursor = connection.cursor()

        create_db_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname))
        cursor.execute(create_db_query)
    except psycopg2.Error as e:
        ...
    finally:
        if connection:
            cursor.close()
            connection.close()




def auto_migrates(dbname, user, password, host="localhost", port="5432"):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()

        try:
            cur.execute("ALTER TABLE users ADD COLUMN video_gens BIGINT DEFAULT 0;")
            ...
        except psycopg2.errors.DuplicateColumn:
            ...
        except Exception as e:
            ...

        cur.close()
        conn.close()
    except Exception as e:
        ...
