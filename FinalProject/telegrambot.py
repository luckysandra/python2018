import flask
import telebot
import os
import main_code as code
from pymystem3 import Mystem
import pymorphy2
import re

TOKEN = os.environ["TOKEN"]
telebot.apihelper.proxy = {'https': 'socks5h'
                                    '://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(TOKEN, threaded=False)
mystem = Mystem()
morphy = pymorphy2.MorphAnalyzer()
rus = re.compile('[а-я]+-*[а-я]*')
bot.remove_webhook()
bot.set_webhook(url="https://elegic-distich.herokuapp.com/bot")
app = flask.Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """ Sends a welcome message to chat. """
    bot.send_message(message.chat.id, "Я умею делать "
                                      "из ваших слов элегические дистихи.")
    bot.send_message(message.chat.id, "Введите любое русское слово: ")
    bot.send_message(message.chat.id, "Информация для проверяющих: я "
                                      "построен на библиотеке pymorphy, "
                                      "поэтому я специфически паршу слова.")


@bot.message_handler(content_types=['text'])
def send_distich(message):
    """ It seemed fascinated by cats. So I added a check for num of
    pending updates. Now works as well as the main code """
    bot.send_message(message.chat.id, 'Обрабатываю слово %s. Говорю это '
                                      'потому, что иногда я очень долго '
                                      'генерирую для вас дистих! не беспоко'
                                      'йтесь, всё в процессе!' % message.text)
    strin = code.working_horsie(message.text, morphy, mystem, rus)
    bot.reply_to(message, strin)


@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # written with help from Ivan Torubarov
        try:
            webhook_info = bot.get_webhook_info()
            if webhook_info.pending_update_count > 1:  # Vanya u r a godsend
                print('Unwanted updates stopped: ',
                      str(webhook_info.pending_update_count))
                return ''
            else:
                print('Processing new update')
                bot.process_new_updates([update])
        except Exception as e:
            print('%s occured' % str(e))
            pass
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
