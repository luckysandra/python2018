import re
import os
import urllib.request
import urllib.error
from bs4 import BeautifulSoup


# Служебная функция, открывает файл и пускает его в суп
def opener(link):
    try:
        a = urllib.request.urlopen(link)
    # примерно на 14000 файле эта штука ломается несмотря на исключения
    except TimeoutError or urllib.error.HTTPError or urllib.error.URLError:
        file = 'Скачивание не получилось'
        file = BeautifulSoup(file, 'html.parser')
    else:
        file = a.read()
        file = BeautifulSoup(file, 'html.parser')
    return file


# Достаю ссылки на номера газеты
def getting_volumes(startlink):
    volumes = []
    i = 0
    link = startlink + '/archive'
    regvolume = re.compile('item">\s<a data-url="" href="(.+?)"')
    while True:  # ради реюзабельности сделала, чтоб листал, пока листается
        i += 1
        page = link + '?page=' + str(i)
        page = str(opener(page))
        links = regvolume.findall(page)
        if links:
            for sublink in links:
                volume = startlink + sublink
                volumes.append(volume)
        else:
            break
    return volumes


# Достаю ссылки на отдельные статьи
def getting_articles(volumes, startlink):
    articles = []
    regarticle = re.compile('caption-sm">\s<a href="(.+?)"')
    for volume in volumes:
        volume = str(opener(volume))
        a = regarticle.findall(volume)
        # здесь возможно нужно такое же условие, как и выше
        for sublink in a:
            article = startlink + sublink
            articles.append(article)
    return articles


# Я не придумала, как умнее конвертировать даты из слов в числа
def months(string):
    # есть еще вариант через .startswith(), но там проблема с мартом и маем
    if string == 'января':
        string = '01'
    elif string == 'февраля':
        string = '02'
    elif string == 'марта':
        string = '03'
    elif string == 'апреля':
        string = '04'
    elif string == 'мая':
        string = '05'
    elif string == 'июня':
        string = '06'
    elif string == 'июля':
        string = '07'
    elif string == 'августа':
        string = '08'
    elif string == 'сентября':
        string = '09'
    elif string == 'октября':
        string = '10'
    elif string == 'ноября':
        string = '11'
    elif string == 'декабря':
        string = '12'
    return string


# Этой функцией я собираю метаинформацию про каждую статью
def meta(article):
    # в моей газете нет категорий и авторов
    # я ищу только текст статьи, название, дату создания
    article = str(opener(article))
    try:
        header = re.search('<h2>(.+?)</h2>', article).group()
        header = re.findall('<h2>(.+?)</h2>', header)[0]
        created = re.findall('№ \d+, (.+?)</a>', article)
        for i, c in enumerate(created):
            day = re.search('\d+', c).group()
            month = re.search('\D+', c).group()
            month = months(month.strip().strip(','))
            year = re.search(', \d+', c).group()
            year = year.strip(',').strip()
        date = day + '.' + month + '.' + year
        # если я потом придумаю, как чистить, я залью ещё один файл
        # с чистильщиком, автоматически гуляющим по директории
        text = article
    except AttributeError:
        header, date, day, month, year, text = 'None', 'None', 'None', 'None', 'None', 'None'
    return header, date, day, month, year, text


# Эта функция создает или дополняет мета-файл
def metafile(path, page, link, deleter):
    header, date, day, month, year, text = page
    meta_cort = (path, header, date, link, year)
    meta_string = '%s\tNone\t%s\t%s\tпублицистика\tNone\tнейтральный\tн-возраст\t' \
                  'н-уровень\tобластная\t%s\tКрасный Север\t%s\tгазета\tРоссия\t' \
                  'Вологодский регион\tru\n' % meta_cort
    directory = './gazety'
    meta_file = os.path.join(directory, 'metadata.csv')
    if not deleter:
        if not os.path.exists(meta_file):
            meta_1 = 'path\tauthor\theader\tcreated\tsphere\ttopic\tstyle\t' \
                     'audience_age\taudience_level\taudience_size\tsource\t' \
                     'publication\tpubl_year\tmedium\tcountry\tregion\tlanguage\n'
            with open(meta_file, 'w', encoding='utf-8') as f:
                f.write(meta_1)
            with open(meta_file, 'a', encoding='utf-8') as f:
                f.write(meta_string)
        else:
            a = False
            with open(meta_file, 'r', encoding='utf-8') as f:
                if meta_string not in f:
                    a = True
            if a:
                with open(meta_file, 'a', encoding='utf-8') as f:
                    f.write(meta_string)
    else:
        # нашла решение для проблемы, когда почему-то теряется формат файла
        with open(meta_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(meta_file, 'w', encoding='utf-8') as f:
            f.writelines(item for item in lines[:-1])


# У меня почему-то стрип плохо чистит, поэтому делаю функцию
def adv_stripping(string):
    string = string.replace('?', '"')
    string = string.replace('"', '!')
    string = string.replace('!', '.')
    string = string.replace('/', '')
    string = string.replace('.', '')
    string = string.replace('*', '')
    string = string.replace('<', '>')
    string = string.replace(':', '')
    string = string.replace('\ ', '')
    return string


# Эта функция создает файловую структуру
def fileconst(page, link):
    header, date, day, month, year, text = page
    for_article = ('None', header, date, 'None', link, text)
    article = '@au %s @ti %s @da %s @topic %s @url %s\n\%s' % for_article
    directory = './gazety'
    dname = os.path.join(directory, 'plain', year, month, day)
    if not os.path.exists(dname):
        os.makedirs(dname)
    header = adv_stripping(header)
    path_1 = header + '.txt'
    path = os.path.join(dname, path_1)
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(article)
        except OSError:
            print('Не получилось создать ',path_1)
    deleter = False
    metafile(path, page, link, deleter)

# я не смогла заставить его работать
# def first_run(startlink):
#     path = 'articles.txt'
#     if not os.path.exists(path):
#         print('Качаю ссылки на номера газеты')
#         volumes = getting_volumes(startlink)
#         print('Скачал номера, качаю ссылки на статьи')
#         articles = getting_articles(volumes, startlink)
#         with open(path, 'w', encoding='utf-8') as f:
#             for link in articles:
#                 f.writelines(link)
#                 f.writelines('\n')
#         print('Теперь у вас есть все нужные ссылки')
#     else:
#         print('Получил нужные мне ссылки')


# А вот основная функция, запускающая краулер и создающая файловую систему
def main():
    print('Эта программа создаст у Вас на компьютере файловую систему.')
    print('Убедитесь в том, что у Вас есть хотя бы 5 Гигабайт дискового пространства')
    startlink = 'http://krassever.ru'
    print('Качаю ссылки на номера газеты')
    # with open('articles.txt', 'r', encoding='utf-8') as f:
    #   articles = f.readlines()
    volumes = getting_volumes(startlink)
    print('Скачал номера, качаю ссылки на статьи. Это занимает ~ 10 минут,'
          'так что можете пока заварить себе чаю :)')
    articles = getting_articles(volumes, startlink)
    print('Всё скачал!')
    a = input('Погнали? Если да, нажмите Enter. Если нет, введите любой символ: ')
    while a == '':
        n = 0
        for link in articles:
            # link = link.strip('\n')
            page = meta(link)
            fileconst(page, link)
            # alternative
            # fileconst выдает path_1, header и path и дальше происходит
            # if path_1 != 'header' + 'txt':
            #   deleter = True
            #   metafile(path, page, link, deleter)
            #   os.remove(path)
            # я пыталась решить проблему файлов без расширения
            n += 1
            print(n)
        print('Я скачал ', n, 'из', len(articles), 'страниц')
        a = input('Могу пройтись ещё раз. Скачанные файлы не удалятся (да = Enter)')


if __name__ == '__main__':
    main()
