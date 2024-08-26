import time
import pika
import logging

# Настройка логирования
logging.basicConfig(
    filename='worker.log',  # Имя файла лога
    level=logging.INFO,     # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат записи
)

def callback(ch, method, properties, body):
    logging.info(f"Received {body.decode()}")  # Запись в лог
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'password')))
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.error("RabbitMQ not ready, retrying in 5 seconds...")
            time.sleep(5)

connection = connect_to_rabbitmq()

channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

logging.info('Waiting for messages...')
channel.start_consuming()
