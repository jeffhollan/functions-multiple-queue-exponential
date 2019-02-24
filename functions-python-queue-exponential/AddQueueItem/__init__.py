import logging

import azure.functions as func


def main(req: func.HttpRequest,
         msg: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    msg.set('python queue message')

    return func.HttpResponse('Message sent')
