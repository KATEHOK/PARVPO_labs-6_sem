import time
import pika
import logging
import psycopg2
from psycopg2 import sql


# Настройка логирования
logging.basicConfig(
    # filename='/var/log/worker.log',  # Имя файла лога
    level=logging.DEBUG,     # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат записи
    datefmt='%Y-%m-%d %H:%M:%S'      # Формат даты и времени
)

def save_to_db(connection, data):
    try:
        with connection.cursor() as cursor:
            query = sql.SQL("INSERT INTO messages (content) VALUES (%s)")
            cursor.execute(query, (data,))
            connection.commit()
    except Exception as e:
        logging.error(f"Failed to save data to DB: {e}")
        # print(f"Failed to save data to DB: {e}")

def callback(ch, method, properties, body):
    logging.info(f"Received {body.decode()}")  # Запись в лог
    # print(f"Received {body.decode()}")

    # обработка заявок
    save_to_db(db_connection, body.decode())
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'password')))
            logging.info(f"Connected to the RabbitQM")  # Запись в лог
            # print(f"Connected to the RabbitQM")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.error("RabbitMQ not ready, retrying in 5 seconds...")
            # print("RabbitMQ not ready, retrying in 5 seconds...")
            time.sleep(5)

def connect_to_db():
    while True:
        try:
            connection = psycopg2.connect(dbname='mydatabase', user='myuser', password='mypassword', host='db')
            logging.info(f"Connected to the PostgreSQL")  # Запись в лог
            # print(f"Connected to the PostgreSQL")
            return connection
        except psycopg2.OperationalError:
            logging.error("PostgreSQL not ready, retrying in 5 seconds...")
            # print("PostgreSQL not ready, retrying in 5 seconds...")
            time.sleep(5)

connection = connect_to_rabbitmq()
db_connection = connect_to_db()

channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

logging.info('Waiting for messages...')
# print('Waiting for messages...')
channel.start_consuming()
