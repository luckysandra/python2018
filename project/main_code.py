from pymystem3 import Mystem
import pymorphy2
import json
import os
import random
import re
import gensim
import requests
import logging
logging.basicConfig(filename="sample.log", level=logging.INFO)


def download_file(url):
    """ Downloads the binary from RusVectores """
    # code partially taken from StackOverflow
    filename = url.split('/')[-1]
    file = requests(url, allow_redirects=True)
    with open(filename, 'wb') as f:
        f.write(file.content)
    return filename


# Searching the directory for a bin.gz binary
def checking_for_file():
    directory = os.listdir(os.getcwd())
    for i in directory:
        if i.endswith('vec.gz') or i.endswith('bin.gz'):
            return i
    # I'm using this binary as it's the last mystem-based one
    m = download_file("http://rusvectores.org/static/models/"
                      "rusvectores2/ruscorpora_mystem_cbow_300_2_2015.bin.gz")
    return m


def my_stem(string):
    """ Receives the string, returns it's tagsets and lemmas """
    mystm = Mystem()
    string_gr = json.dumps(mystm.analyze(string), ensure_ascii=False)
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


# Searches a corpus and finds random lines
def get_string():
    """ Takes two random strings from a file,
    returns words from it and the string itself """
    with open('elegic_distikhs.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
    n = random.randint(0, len(text)-2)
    string = text[n] + text[n+1]
    words = []
    for word in string.lower().split():
        wordie = re.search('[а-я]+-*[а-я]*', word)
        if wordie:
            words.append(wordie.group())
    return words, string


# Takes a string and returns its vowel count
def vowels(string):
    """ Takes a string and returns its number of syllables """
    vowel_list = ('а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я')
    k = 0
    for char in string:
        if char in vowel_list:
            k += 1
    return k


# Puts the word into the string
def new_string(wordie, words, string, morphy):
    """ Takes a string and puts the word in it """
    new_str = ''
    string_gr = frozenset()
    full_gr = {}
    new_word = ''
    pos = re.search('[а-я]+-*[а-я]*', wordie)
    if pos:
        pos = morphy.parse(pos.group())[0].tag.POS
    for i, word in enumerate(words):
        tag = morphy.parse(word)[0].tag
        if pos == tag.POS:
            gramm = str(morphy.parse(word)[0].tag)
            gramm = gramm.replace(',', ' ').split(' ')
            grammems = []
            for item in gramm:
                if morphy.parse(wordie)[0].inflect({item}) is not None:
                    grammems.append(item)  # only the 'good' tags
            string_gr = frozenset(tuple(grammems))
            try:
                new_word = morphy.parse(wordie)[0].inflect(string_gr).word
                if vowels(new_word) == vowels(word):
                    new_str = string.replace(word, new_word)
                    words.remove(word)
                    words.insert(i, new_word)
                    word = new_word
            except AttributeError:
                pass
        full_gr[word] = frozenset(tuple(str(tag).replace(',', ' ').split(' ')))
    return new_str, new_word, full_gr, string_gr


def load_model(m):
    if m.endswith('bin.gz'):
        return gensim.models.KeyedVectors.load_word2vec_format(m,
                                                               binary=True)
    elif m.endswith('vec.gz'):
        return gensim.models.KeyedVectors.load_word2vec_format(m,
                                                               binary=False)
    else:
        print('Unable to read vector space')
        return None


def word2vec_words(model, words):
    """ Takes a model, a list of words and the input
    and turns it into a new string with different words"""
    wordies = []
    for word in words:
        clean_word = re.search('[а-я]+', word).group()
        if word in model:
            for item in model.most_similar(positive=word, topn=10):
                ending = re.search('_[A-Z]+', word).group()
                it = re.search('[а-я]+', item[0])
                try:
                    it = it.group()
                except AttributeError:
                    break
                if item[0].endswith(ending) and \
                        vowels(it) == vowels(clean_word):
                    wordies.append((clean_word, it))
    return wordies


def working_horsie(wordie):
    m = checking_for_file()
    model = load_model(m)
    morphy = pymorphy2.MorphAnalyzer()
    k = 1
    count = 0
    while k:
        words, string = get_string()
        new_str, new_wd, full_gr, string_gr = new_string(wordie, words,
                                                         string, morphy)
        if morphy.parse(wordie)[0].inflect(string_gr).word in new_str:
            words_tagged = my_stem(new_str.lower())
            wordies = word2vec_words(model, words_tagged)
            for item in wordies:
                if item[0] in full_gr:
                    gr_info = full_gr[item[0]]
                    old_word = morphy.parse(item[0])[0].inflect(gr_info)
                    new_word = morphy.parse(item[1])[0].inflect(gr_info)
                    try:
                        new_word = new_word.word
                        old_word = new_word.word
                    except AttributeError:
                        new_word = None
                    if new_word is not None and old_word is not None and \
                            vowels(old_word) == vowels(new_word)\
                            and old_word != new_wd:
                        new_str = new_str.replace(old_word, new_word)
            if not new_str.endswith('.'):
                new_str = new_str.replace(new_str[-3:-2], '.')
                return new_str
            k = 0
        count += 1
        if count > 1076:
            return 'С этим словом я не смогу сделать дистих :('


if __name__ == '__main__':
    word = input('Ваше слово: ')
    string = working_horsie(word)
