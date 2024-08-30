import logging
from flask import Flask, request, render_template, redirect, url_for
import pika
import json

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    # filename='/var/log/webapi.log',  # Путь к файлу для логов
    level=logging.DEBUG,             # Уровень логирования
    format='%(asctime)s %(levelname)s %(message)s',  # Формат логов
    datefmt='%Y-%m-%d %H:%M:%S'      # Формат даты и времени
)

def send_to_queue(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'password')))
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(exchange='', routing_key='task_queue', body=json.dumps(message))
        connection.close()
        logging.info(f"Message sent to queue: {message}")  # Логирование успешной отправки сообщения
        # print((f"Message sent to queue: {message}"))
    except Exception as e:
        logging.error(f"Failed to send message to queue: {e}")  # Логирование ошибки
        # print(f"Failed to send message to queue: {e}")

@app.route('/', methods=['GET'])
def index():
    logging.info("Rendering index page")  # Логирование обращения к главной странице
    # print("Rendering index page")
    return render_template('form.html', message='Форма успешно отправлена!')

@app.route('/send', methods=['POST'])
def send_message():
    message = request.json
    send_to_queue(message)
    logging.info(f"Received message: {message}")  # Логирование полученного сообщения
    # print(f"Received message: {message}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    logging.info(f"Waiting for http-requests...")
    app.run(host='0.0.0.0')
