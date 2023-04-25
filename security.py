import base64
import hashlib
import hmac
import os

def get_x_line_signature(event):
    return event['headers']['x-line-signature'].encode()
    
def get_body_signature(event):
    channel_secret = os.environ['LINE_CHANNEL_SEACRET']
    body = event['body']
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)
    return signature
    
def check_signature(event):
    x_line_signature = get_x_line_signature(event)
    body_signature = get_body_signature(event)
    
    return x_line_signature == body_signature
    
    