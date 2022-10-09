from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
)

import sqlite3 as lite

app = Flask(__name__)

line_bot_api = LineBotApi('5t9S02sHvN0/d0J6ZyiDVpK/qLu+dYNIt5XKK5kuolU55fVEC9zVlFMbIYwa+WQviwxfBCrTsDjTduekho75zZTpFcO2hwf8I+p0cCMM53EiBoMS1n4pbAU/UgwMHw90eTo7CTYAsY3FEMjb3pvMYQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('50b94542aba247e3ae031f7474598903')

@app.route("/")
def  hello():
    return "Hello World!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    #print("request.headers:", request.headers)
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    #print("body:", body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    print("FollowEvent:", event)
    print(event.source.user_id)
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    print(profile.display_name)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.status_message)

    welcome_msg = f"""Hello! {profile.display_name} 您好，歡迎您加入 '143572 Python自動化line機器人與資料庫整合實務班' 課程！
請問您有什麼需求可以為您服務?"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg))

@handler.add(event=UnfollowEvent)
def handle_unfollow(event):
    print("unfollow:", event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "#新聞":
        title = []
        link = []
        piclink= []
        publishat = []
        con = lite.connect(r"C:\python\linebot\news.sqlite")
        cur = con.cursor()
        rd = cur.execute("select * from 鉅亨網新聞;")
        for row in rd:
            publishat.append(row[1])
            title.append(row[2])
            link.append(row[4])
            piclink.append(row[5])
        cur.close()
        con.close()

        msg = ''
        for dt, tt, l, picl in zip(publishat[:10], title[:10], link[:10], piclink[:10]):
            msg += dt + '  ' + tt + '\n' + l + '\n' + picl + '\n\n'
        print(msg)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


if __name__ == "__main__":
    app.run()