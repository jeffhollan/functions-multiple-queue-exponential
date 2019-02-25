import logging

import azure.functions as func
from azure.servicebus.aio import ServiceBusClient, QueueClient, Message
import os, time
from datetime import datetime, timedelta

RETRY_LIMIT = 5
RETRY_MULTIPLIER_SECONDS = 5

connection_str = os.environ['ServiceBusConnectionString']
sb_client = ServiceBusClient.from_connection_string(connection_str)
queue_client = sb_client.get_queue('queue')

async def main(msg: func.ServiceBusMessage):
    try:
        logging.info('Python ServiceBus queue trigger processed message: %s',
                     msg.get_body().decode('utf-8'))
        
        raise Exception('something went wrong')
    except Exception:
        retry_count = int(msg.user_properties['retry-count']) if 'retry-count' in msg.user_properties else 0

        # If there are retries remaining
        if retry_count < RETRY_LIMIT:
            # Calculate a delay of seconds for next message
            retry_count += 1
            delay_seconds = retry_count * RETRY_MULTIPLIER_SECONDS
            logging.info('Scheduling message for the %i retry in %i seconds', retry_count, delay_seconds)

            # Schedule and resend message onto queue
            async with queue_client.get_sender() as sender:
                message = Message(msg.get_body())
                message.message_id = msg.message_id
                message.user_properties = {'original-message-id': msg.message_id, 'retry-count': retry_count}
                enqueue_time = datetime.now() + timedelta(seconds=delay_seconds)
                await sender.schedule(enqueue_time, message)
        else:
            logging.error('Exhausted all retries')
            # Could publish to a queue for poisoned messages