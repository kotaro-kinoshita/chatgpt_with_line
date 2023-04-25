import json
import os
import urllib.request
import logging

from security import check_signature
from chat import ChatGPT

logger = logging.getLogger()
logger.setLevel(logging.INFO)

chat = ChatGPT()

LINE_CHANNEL_ACCESS_TOKEN   = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

REQUEST_URL = 'https://api.line.me/v2/bot/message/reply'
REQUEST_METHOD = 'POST'
REQUEST_HEADERS = {
    'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

REQUEST_MESSAGE = [
    {
        'type': 'text',
        'text': 'こんにちは！'
    }
]

def extract_message(body):
    if body['events'][0]["type"] == "message":
        if body['events'][0]["message"]["type"] == "text":
            return body['events'][0]["message"]["text"] 
    return None

def lambda_handler(event, context):
    logger.info(event)
    
    if not check_signature(event):
        return 0

    body = json.loads(event['body'])
    
    params = {
        'replyToken': body['events'][0]['replyToken'],
        'messages': REQUEST_MESSAGE
    }

    message = extract_message(body)
    
    if message is None:
        return 0

    params['messages'][0]["text"] = chat(message, logger)

    request = urllib.request.Request(
        REQUEST_URL, 
        json.dumps(params).encode('utf-8'), 
        method=REQUEST_METHOD, 
        headers=REQUEST_HEADERS
        )
    response = urllib.request.urlopen(request, timeout=10)
    return 0
