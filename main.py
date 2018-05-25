import os
import sys
import io
import json
import MeCab
import tempfile
import numpy as np



from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    LocationMessage, StickerMessage, FileMessage,
    ButtonsTemplate, URITemplateAction, TemplateSendMessage
)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
app = Flask(__name__)

with open('./data/environment.json', 'r') as f:
    environ = json.load(f)
channel_secret = environ['channel_secret']
channel_access_token = environ['channel_access_token']
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/")
def hello_world():
    return '<a href="http://www.viz.media.kyoto-u.ac.jp/">Koyamada Lab</a>'


@app.route("/test")
def test():
    return '<p>this is test html</p>'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# process text message
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    send_message = get_text_response(event)
    line_bot_api.reply_message(
        event.reply_token,
        send_message
    )


def get_text_response(event):
    text = event.message.text
    if text == 'egrid':
        buttons_template = \
            ButtonsTemplate(title='Interview', text='E-Grid Visualization',
                            actions=[URITemplateAction(
                                label='Go to E-Grid',
                                uri='https://egrid.jp/projects')])
        response_message = TemplateSendMessage(alt_text='E-grid link',
                                               template=buttons_template)
        return response_message
    elif text == 'upload':
        buttons_template = \
            ButtonsTemplate(title='Upload', text='Upload data to database',
                            actions=[URITemplateAction(
                                label='Go to data form',
                                uri='https://yuqingguan.top/upload')])
        response_message = TemplateSendMessage(alt_text='upload link',
                                               template=buttons_template)
        return response_message
    else:
        profile = line_bot_api.get_profile(event.source.user_id)
        reply_text = profile.display_name + ' : '
        tagger = MeCab.Tagger('mecabrc')
        tagger.parse('')
        node = tagger.parseToNode(text)
        while node:
            word = node.surface
            reply_text += (word + ' ')
            node = node.next
        return TextSendMessage(reply_text)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
