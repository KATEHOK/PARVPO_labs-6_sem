from flask import Flask, request, render_template, redirect, url_for
import pika
import json

app = Flask(__name__)

def send_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials('user', 'password')))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='task_queue', body=json.dumps(message))
    connection.close()

@app.route('/', methods=['GET'])
def index():
    return render_template('form.html', message='Форма успешно отправлена!')

@app.route('/send', methods=['POST'])
def send_message():
    message = request.json
    send_to_queue(message)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
