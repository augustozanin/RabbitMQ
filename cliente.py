import pika
import time

# Configurações do RabbitMQ (ajuste o IP se necessário)
RABBITMQ_HOST = '10.1.25.176'  # Ou 'localhost' se for na mesma máquina
FILA_LEITURA = 'fila_leitura'
FILA_RESPOSTA = 'fila_resposta'

# Lista de UIDs autorizados (substitua pelos seus UIDs reais)
UID_AUTORIZADOS = [
    "12345678",  # Exemplo
    "87654321",
    "F35883F5"   # Exemplo
]

# Função para controlar o servo (simulada ou real)
def controlar_cancela(abrir):
    if abrir:
        print("[CANCELA] ABERTA (servo em 90 graus)")
        # Código real para mover o servo (ex.: GPIO do Raspberry)
    else:
        print("[CANCELA] FECHADA (servo em 0 graus)")

# Conexão com o RabbitMQ
try:
    credentials = pika.PlainCredentials('seu_usuario', 'sua_senha')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=FILA_LEITURA)
    channel.queue_declare(queue=FILA_RESPOSTA)
    print("[CONSUMIDOR] Pronto para receber UIDs...")
except Exception as e:
    print(f"[ERRO] Falha ao conectar ao RabbitMQ: {e}")
    exit()

# Função chamada quando um UID é recebido
def callback(ch, method, properties, body):
    uid = body.decode().strip()
    print(f"\n[CONSUMIDOR] UID recebido: {uid}")

    # Verifica autorização
    if uid in UID_AUTORIZADOS:
        resposta = "AUTORIZADO"
        controlar_cancela(abrir=True)  # Abre a cancela
        time.sleep(3)  # Tempo aberto (ajuste conforme necessário)
        controlar_cancela(abrir=False)  # Fecha a cancela
    else:
        resposta = "NEGADO"

    # Envia resposta para o produtor (código original)
    channel.basic_publish(
        exchange='',
        routing_key=FILA_RESPOSTA,
        body=resposta
    )
    print(f"[CONSUMIDOR] Resposta enviada: {resposta}")

# Configura o consumidor
channel.basic_consume(
    queue=FILA_LEITURA,
    on_message_callback=callback,
    auto_ack=True
)

try:
    print("[CONSUMIDOR] Aguardando UIDs... (Pressione Ctrl+C para sair)")
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n[CONSUMIDOR] Encerrando...")
finally:
    connection.close()