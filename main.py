import json
import sys

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)  
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

with open('./data/enviroment.json','r') as f:
    env = json.load(f)
channel_secret = env['channel_secret']
channel_access_token = env['channel_access_token']
if channel_secret is None:
    print('channel_secret is empty')
    sys.exit(1)
if channel_access_token is None:
    print('channel_access_token is empty')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"
    
@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
        
    return 'OK'
    
@handler.add(MessageEvent, message=TextMessage)
def handler_text_message(event):
    text = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")