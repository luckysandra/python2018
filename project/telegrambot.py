import flask
import telebot
import os
import main_code as code
from pymystem3 import Mystem
import pymorphy2
import re

TOKEN = os.environ["TOKEN"]
WEBHOOK_URL_PATH = "/{}/".format(TOKEN)
telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url="https://elegic-distich.herokuapp.com/bot")
app = flask.Flask(__name__)
mystem = Mystem()
morphy = pymorphy2.MorphAnalyzer()
rus = re.compile('[а-я]+-*[а-я]*')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """ Worked but now doesn't work. And when it did, it sent a lot of
    uncalled for messages"""
    try:
        bot.send_message(message.chat.id, "Я умею делать "
                                          "из ваших слов элегические дистихи.")
        bot.send_message(message.chat.id, "Введите любое русское слово: ")
    except telebot.apihelper.ApiException:
        pass


@bot.message_handler(func=lambda m: True, content_types=['text'])
def send_distich(message):
    """ Worked but now doesn't work. And when it did, it sent a lot of
        uncalled for messages. It seems fascinated by cats"""
    string = code.working_horsie(message.text, morphy, rus)
    try:
        bot.send_message(message.chat.id, string)
    except telebot.apihelper.ApiException:
        pass


@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
