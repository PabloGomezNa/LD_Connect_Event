import os
import json
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "ld_exchange")
RABBITMQ_EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE", "fanout")




def publish_event(event_type: str, team_name: dict):
    """
    Publish an event message to RabbitMQ so LD_Eval can consume it.
    :param event_type: e.g., "commit_event", "task_created", etc.
    :param payload: A dictionary with relevant event data.
    """
    # 1. Build connection params
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection_params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )

    # 2. Connect and open a channel
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # 3. Declare exchange (if not already declared)
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE,
                             exchange_type=RABBITMQ_EXCHANGE_TYPE,
                             durable=True)

    # 4. Create the message body
    message = {
        "event_type": event_type,
        "tean_name": team_name
    }
    body = json.dumps(message)

    # 5. Publish the message
    channel.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key="",   # not used for fanout, or set if using direct/topic
        body=body
    )

    # 6. Close the connection
    connection.close()
