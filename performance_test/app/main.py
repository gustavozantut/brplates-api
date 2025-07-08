import time
import requests
import psycopg2
from pathlib import Path
import os
from dotenv import load_dotenv

# 📁 Carrega variáveis do .env
load_dotenv()

# 🔐 Conexão com o banco
conn = psycopg2.connect(
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=os.environ.get("POSTGRES_PORT", 5432),
)
cursor = conn.cursor()

# 📁 Configurações
API_URL = "http://api:8000/api/v1/processar-placa"
NUM_REQUESTS = int(os.environ["NUM_REQUESTS_PERFORMANCE_TEST"])
IS_CELERY = True
IMAGE_PATH = os.path.join(os.getenv("YOLO_OUTPUT_DIR"), "imagem_teste.jpg")
headers = {"X-API-Key": os.getenv("API_KEY_PERFORMANCE_TEST")}


def medir_requisicao(i):
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": (IMAGE_PATH, f, "image/jpeg")}
        inicio = time.perf_counter()
        response = requests.post(API_URL, files=files, headers=headers)
        fim = time.perf_counter()
        tempo = fim - inicio
        print(f"#{i} - Status: {response.status_code} - Tempo: {tempo:.2f}s")

        # Gravar no banco
        cursor.execute(
            """
            INSERT INTO request_logs (indice, status_code, tempo_segundos, celery)
            VALUES (%s, %s, %s, %s)
            """,
            (i, response.status_code, round(tempo, 4), IS_CELERY),
        )
        conn.commit()


def main():
    for i in range(1, NUM_REQUESTS + 1):
        medir_requisicao(i)

    print(f"\n✅ Todos os registros foram gravados no banco.")


if __name__ == "__main__":
    if not Path(IMAGE_PATH).exists():
        print(f"❌ Imagem {IMAGE_PATH} não encontrada.")
    else:
        try:
            main()
        finally:
            cursor.close()
            conn.close()
