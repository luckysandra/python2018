from pymystem3 import Mystem
from tqdm import tqdm
import pymorphy2
import json
import os
import requests
import random
import re
import logging
import gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def download_file(url):
    """ Downloads the binary from RusVectores """
    # code partially taken from StackOverflow
    filename = url.split('/')[-1]
    file = requests.get(url, allow_redirects=True)
    with open(filename, 'wb') as f:
        f.write(file.content)
    return filename


# Searching the directory for a bin.gz binary
def checking_for_file():
    directory = os.listdir(os.getcwd())
    for i in directory:
        if i.endswith('vec.gz') or i.endswith('bin.gz'):
            print('Already have the binary')
            return i
    print('Downloading the binary')
    # I'm using this binary as it's the last mystem-based one
    m = download_file("http://rusvectores.org/static/models/"
                      "rusvectores2/ruscorpora_mystem_cbow_300_2_2015.bin.gz")
    print('Got it')
    return m


# Returns a list of tagged words, ready to be used in a Mystem or Universal Tags model
def my_stem(string):
    """ Receives the string, returns it's tagsets and lemmas """
    mystm = Mystem()
    string_gr = json.dumps(mystm.analyze(string), ensure_ascii=False)   # makes a list of mystem grammems
    string_gr = json.loads(string_gr)
    words_tagged = []
    for i in tqdm(string_gr):
        try:
            tag = re.search('[a-zA-Z]+-*[a-zA-Z]*',
                            i['analysis'][0]['gr'].split(',')[0]).group()
            words_tagged.append(i['analysis'][0]['lex'] + '_' + tag)
        except KeyError:
            pass
    return words_tagged     # returns a list of words ready to be used in a model


# Searches a corpus and finds random lines
def get_string():
    """ Takes two random strings from a file, returns words from it and the string itself """
    with open('elegic_distikhs.txt', 'r', encoding='utf-8') as f:
        text = f.readlines()
    n = random.randint(0, len(text)-1)  # finds a random string
    string = text[n] + text[n+1]    # glues the string and its subsequent string together
    words = []
    for word in string.lower().split():
        wordie = re.search('[а-я]+-*[а-я]*', word)
        if wordie:
            words.append(wordie.group())
    return words, string     # returns all words from the string and the string itself


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
    POS = morphy.parse(wordie)[0].tag.POS
    for i, word in enumerate(words):
        tag = morphy.parse(word)[0].tag
        if POS == tag.POS:
            gramm = str(morphy.parse(word)[0].tag)
            gramm = gramm.replace(',', ' ').split(' ')
            grammems = []
            for item in gramm:
                if morphy.parse(wordie)[0].inflect({item}) is not None:
                    grammems.append(item)  # only the 'good' tags
            string_gr = frozenset(tuple(grammems))
            new_word = morphy.parse(wordie)[0].inflect(string_gr).word
            if vowels(new_word) == vowels(word):
                new_str = string.replace(word, new_word)
                words.remove(word)
                words.insert(i, new_word)
                word = new_word
        full_gr[word] = frozenset(tuple(str(tag).replace(',', ' ').split(' ')))
    return new_str, new_word, full_gr, string_gr


def word2vec_words(m, words):
    """ Takes a model, a list of words and the input
    and turns it into a new string with different words"""
    wordies = []
    if m.endswith('bin.gz'):
        model = gensim.models.KeyedVectors.load_word2vec_format(m,
                                                                binary=True)
    elif m.endswith('vec.gz'):
        model = gensim.models.KeyedVectors.load_word2vec_format(m,
                                                                binary=False)
    else:
        print('Unable to read vector space')
        return None
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
                if item[0].endswith(ending) and vowels(it) == vowels(clean_word):
                    wordies.append((clean_word, it))
    return wordies


def working_horsie():
    m = checking_for_file()
    wordie = input('Ваше слово: ')
    morphy = pymorphy2.MorphAnalyzer()
    k = 1
    while k:
        words, string = get_string()
        new_str, new_wd, full_gr, string_gr = new_string(wordie, words, string, morphy)
        if morphy.parse(wordie)[0].inflect(string_gr).word in words:
            words_tagged = my_stem(new_str.lower())
            wordies = word2vec_words(m, words_tagged)
            for item in wordies:
                if item[0] in full_gr:
                    gr_info = full_gr[item[0]]
                    old_word = morphy.parse(item[0])[0].inflect(gr_info).word
                    new_word = morphy.parse(item[1])[0].inflect(gr_info)
                    try:
                        new_word = new_word.word
                    except AttributeError:
                        new_word = None
                    if new_word is not None and vowels(old_word) == vowels(new_word) and old_word != new_wd:
                        new_str = new_str.replace(old_word, new_word)
            break
    print(new_str)
        #print(string)


if __name__ == '__main__':
    main()
