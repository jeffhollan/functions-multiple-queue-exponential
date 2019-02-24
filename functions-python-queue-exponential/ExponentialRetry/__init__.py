import logging

import azure.functions as func
from azure.servicebus.aio import ServiceBusClient, QueueClient, Message
import os

connection_str = os.environ['ServiceBusConnectionString']
sb_client = ServiceBusClient.from_connection_string(connection_str)
queue_client = sb_client.get_queue('queue')

async def main(msg: func.ServiceBusMessage):
    try:
        logging.info('Python ServiceBus queue trigger processed message: %s',
                     msg.get_body().decode('utf-8'))
        retry_count = msg.user_properties['retry-count']
        if retry_count is None:
            logging.info('my first try on message')
        else:
            logging.info('retry_count: %s', retry_count)
        
        raise Exception('something went wrong')
    except Exception:
        async with queue_client.get_sender() as sender:
            message = Message(msg.get_body())
            message.message_id = msg.message_id
            message.user_properties = {'original-message-id': msg.message_id, 'retry-count': 1}
            await sender.send(message)