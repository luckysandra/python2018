import flask
import telebot
import os
import main_code as code
from pymystem3 import Mystem
import pymorphy2
import re

TOKEN = os.environ["TOKEN"]
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
    strin = code.working_horsie(message.text, morphy,  mystem, rus)
    try:
        bot.send_message(message.chat.id, strin)
    except telebot.apihelper.ApiException:
        pass


message = None


@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        try:
            bot.process_new_updates([update]) # doesn't work and die when 403
            return ''
        except telebot.apihelper.ApiException:
            flask.abort(403)
    else:
        flask.abort(403)


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
