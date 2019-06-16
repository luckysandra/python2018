from pymystem3 import Mystem
import pymorphy2
import json
import os
import random
import re
import gensim
import requests


def download_file(url):
    """ Downloads the binary from RusVectores """
    # code partially taken from StackOverflow
    filename = url.split('/')[-1]
    file = requests.get(url, allow_redirects=True)
    with open(filename, 'wb') as f:
        f.write(file.content)
    return filename


def checking_for_file():
    """ Searches the directory for a bin.gz or vec.gz """
    directory = os.listdir(os.getcwd())
    for i in directory:
        if i.endswith('vec.gz') or i.endswith('bin.gz'):
            return i
    # I'm using this binary as it's the last mystem-based one
    fi = download_file("http://rusvectores.org/static/models/rusvectores2/"
                       "ruscorpora_mystem_cbow_300_2_2015.bin.gz")
    return fi


def load_model(file):
    """ Preloads the Word2Vec model"""
    if file.endswith('bin.gz'):
        return gensim.models.KeyedVectors.load_word2vec_format(m,
                                                               binary=True)
    elif file.endswith('vec.gz'):
        return gensim.models.KeyedVectors.load_word2vec_format(m,
                                                               binary=False)
    else:
        print('Unable to read vector space')
        return None


def my_stem(str_ing, mys_tem):
    """ Receives the string, returns it's tagsets and lemmas """
    string_gr = json.dumps(mys_tem.analyze(str_ing), ensure_ascii=False)
    string_gr = json.loads(string_gr)
    words_tagged = []
    for i in string_gr:
        try:
            tag = re.search('[a-zA-Z]+-*[a-zA-Z]*',
                            i['analysis'][0]['gr'].split(',')[0]).group()
            words_tagged.append(i['analysis'][0]['lex'] + '_' + tag)
        except KeyError:
            pass
    return words_tagged


def vowels(str_ing):
    """ Takes a string and returns its number of syllables """
    vowel_list = ('а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я')
    k = 0
    for char in str_ing:
        if char in vowel_list:
            k += 1
    return k


def word2vec_words(model, words, rus):
    """ Takes a model, a list of words and the input
    and turns it into a new string with different words"""
    preliminary = {}
    for word in words:
        clean_word = re.search(rus, word).group()
        if word in model:
            wordies = []
            for item in model.most_similar(positive=word, topn=100):
                ending = re.search('_[A-Z]+', word).group()
                it = re.search(rus, item[0])
                try:
                    it = it.group()
                except AttributeError:
                    break
                if item[0].endswith(ending) and \
                        vowels(it) == vowels(clean_word):
                    wordies.append(it)
            word = re.search(rus, word).group()
            preliminary[word] = wordies
        else:
            word = re.search(rus, word).group()
            preliminary[word] = []
    return preliminary


def generate_file(mys_tem, model, rus):
    """Makes a JSON item as well as a .txt file to read from"""
    with open('elegic_distikhs.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
    d = {}
    for i, line in enumerate(text):
        print('generating mystem string: ', i + 1)
        words_tagged = mys_tem(line, mys_tem)
        preliminary = word2vec_words(model, words_tagged, rus)
        if not os.path.exists('lemmatized.txt'):
            with open('lemmatized.txt', 'w', encoding='utf-8') as f:
                f.write(str(preliminary))
                f.write('\n')
        else:
            with open('lemmatized.txt', 'a', encoding='utf-8') as f:
                f.write(str(preliminary))
                f.write('\n')
        d[i] = preliminary
    if not os.path.exists('lemmatized.json'):
        f = open('lemmatized.json', 'w', encoding='utf-8')
        json.dump(d, f, ensure_ascii=False, indent=4)


def get_string(rus):
    """ Takes two random strings from a file,
    returns words from it and the string itself """
    with open('elegic_distikhs.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
    n = random.randint(0, len(text) - 2)
    str_ing = text[n] + text[n + 1]
    words = []
    for word in str_ing.lower().split():
        word_1 = re.search(rus, word)
        if word_1:
            words.append(word_1.group())
    return words, str_ing, n


def new_string(word_1, words, str_ing, morphy_class):
    """ Takes a string and puts the word in it """
    new_str = ''
    string_gr = frozenset()
    full_gr = {}
    new_word = ''
    pos = re.search('[а-я]+-*[а-я]*', word_1.lower())
    if pos:
        pos = morphy_class.parse(pos.group())[0].tag.POS
    for i, word in enumerate(words):
        tag = morphy_class.parse(word)[0].tag
        if pos == tag.POS:
            gramm = str(morphy_class.parse(word)[0].tag)
            gramm = gramm.replace(',', ' ').split(' ')
            grammems = []
            for item in gramm:
                if morphy_class.parse(word_1)[0].inflect({item}) is not None:
                    grammems.append(item)  # only the good tags
            string_gr = frozenset(tuple(grammems))
            try:
                new_word = morphy_class.parse(word_1)
                new_word = new_word[0].inflect(string_gr).word
                if vowels(new_word) == vowels(word):
                    boundary = re.compile(r'[а-яА-ЯёЁ]+\B%s\B[а-яА-ЯЁё]+' % word)
                    check = re.search(boundary, str_ing)
                    if check:
                        pass
                    else:
                        new_str = str_ing.replace(word, new_word)
                        words.remove(word)
                        words.insert(i, new_word)
                        word = new_word
            except AttributeError:
                pass
            full_gr[word] = frozenset(tuple(str(tag).replace(',', ' ').
                                            split(' ')))
    return new_str, new_word, full_gr, string_gr


def replacer(word, friends, full_gr, new_str, mor_phy, rus):
    """ Does some magic with word2vec-ed words """
    new_word = ''
    old_word = ''
    for friend in friends:
        if word in full_gr:
            gr_info = full_gr[word]
            old_word = mor_phy.parse(word)[0].inflect(gr_info)
            friend = re.search(rus, friend)
            if friend:
                friend = friend.group()
                new_word = mor_phy.parse(friend)[0].inflect(gr_info)
        try:
            new_word = new_word.word
        except AttributeError:
            new_word = None
        try:
            old_word = old_word.word
        except AttributeError:
            old_word = None
        if new_word is not None and old_word is not None and \
                vowels(old_word) == vowels(new_word) \
                and old_word != new_word:
            new_str = new_str.replace(old_word, new_word)
    return new_str


def dottize(str_in):
    if str_in[-3] in [';', ',', ':', '-', '—', '\\', '/', '\'']:
        str_in = str_in[:-3] + '.\n'
    elif str_in[-3] not in ['.', '!', '?']:
        str_in = str_in[:-2] + '.\n'
    return str_in


def working_horsie(word_1, morphy_class, mystem_class, rus):
    k = 1
    count = 0
    try:
        word_1 = word_1.lower()  # проверяет, всё ли буквы
    except AttributeError:
        return 'Странные у вас символы, я с такими не дружу...'
    wor = re.search(r'\d+', word_1)  # должно ловить цифры в слове
    if wor:
        return 'Кажется, это какие-то цифры. Дистих не получится...'
    wor = re.search(r'[а-яё]+\s[а-яё]*', word_1.lower())  # словосочетания
    if wor:
        return 'Кажется, это словосочетание. Я часто от них ломаюсь, ' \
                'поэтому мне запретили их есть. Не получится дистих :('
    wor = re.search(rus, word_1.lower())  # проверяет русскость
    try:
        wor = wor.group()
    except AttributeError:
        return 'Кажется, это не русские буквы. Я только такие понимаю!'
    if word_1 != wor:  # не реагирует на запросы типа ?слово
        return 'Кажется, в Вашем запросе есть посторонние символы. ' \
               'Не видать нам шедевров нового Гандлевского :('
    # основной код
    while k:
        words, str_ing, num = get_string(rus)  # рандомная строка из корпуса
        new_str, new_wd, full_gr, string_gr = new_string(word_1, words,
                                                         str_ing, morphy_class)
        try:
            word = morphy_class.parse(word_1)[0].inflect(string_gr).word
            if word in new_str:
                # we now have a good string and can actually go home u kno
                with open('lemmatized.json', 'r', encoding='utf-8') as f:
                    text = json.load(f)
                string_1 = text[str(num)]
                string_2 = text[str(num + 1)]
                for item in words:
                    try:
                        item = mystem_class.lemmatize(item)[0]
                        try:
                            new_str = replacer(item, string_1[item], full_gr,
                                               new_str, morphy_class, rus)
                        except KeyError:
                            pass
                        try:
                            new_str = replacer(item, string_2[item], full_gr,
                                               new_str, morphy_class, rus)
                        except KeyError:
                            pass
                    except TypeError or RuntimeError:
                        pass
                # all of the above code is supposed to persuade mystem to
                # change all words in our string to smth else
                if new_str is not None:
                    new_str = dottize(new_str)
                    k = 0
                    return new_str
        except AttributeError:
            pass
        count += 1
        if count > 1076:
            return 'То ли это какое-то редкое слово, то ли я глупенький. ' \
                   'Я очень старался, но дистих не получился :('


def main():
    rus = re.compile(r'\b[а-я]+-*[а-я]*\b')
    morphy_class = pymorphy2.MorphAnalyzer()
    mystem_class = Mystem()
    if not os.path.exists('lemmatized.txt'):
        print('loaded mystem, checking for model')
        m = checking_for_file()
        print('found model, loading')
        model = load_model(m)
        mystem_class = Mystem()
        generate_file(mystem_class, model, rus)
    return morphy_class, rus, mystem_class


if __name__ == '__main__':
    morphy, russian, mystem = main()
    wordie = 'так'
    strin = working_horsie(wordie, morphy, mystem, russian)
    print(strin)
