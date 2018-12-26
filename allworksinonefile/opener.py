import urllib.request
from bs4 import BeautifulSoup
import re
import json
import os
from socket import timeout

# Открываем ссылку
def opener(link):
    try:
        a = urllib.request.urlopen(link)
        file = a.read().decode('utf-8')
        file = BeautifulSoup(file, 'html.parser')
        print('yay')
    except TimeoutError or timeout:
        file = None
        print('nay')
    return file

# Этой функцией я собираю метаинформацию про каждую статью
def meta(article):
    # в моей газете нет категорий и авторов
    # я ищу только текст статьи, название, дату создания
    soup = opener(article)
    #try:
        #header = re.search('<h2>(.+?)</h2>', article).group()
        #header = re.findall('<h2>(.+?)</h2>', header)[0]
        #created = re.findall('№ \d+, (.+?)</a>', article)
        #for i, c in enumerate(created):
        #    day = re.search('\d+', c).group()
        #    month = re.search('\D+', c).group()
        #    #month = months(month.strip().strip(','))
        #    year = re.search(', \d+', c).group()
        #    year = year.strip(',').strip()
        #date = day + '.' + month + '.' + year
        # если я потом придумаю, как чистить, я залью ещё один файл
        # с чистильщиком, автоматически гуляющим по директории
    text = soup.get_text(article)
    #except AttributeError:
        #header, date, day, month, year, text = 'None', 'None', 'None', 'None', 'None', 'None'
    return text

def main():
    article = 'http://krassever.ru/article/usilivat-nuzhno-ne-tol-ko-okhranu-no-i-chelovechnost'
    text = meta(article)
    print(meta(article))


main()