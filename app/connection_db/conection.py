import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="minha_farmacinha",
        user="postgres",
        password="admin"
    )
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("Conexão com PostgreSQL bem-sucedida!")
    cur.close()
except psycopg2.Error as e: 
    print(f"Erro ao conectar ao banco de dados: {e}")