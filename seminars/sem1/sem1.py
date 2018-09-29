import collections
import random

#Функция для открытия файлов
def opener(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        text = f.readlines()
    return text

#Делаем чистый словарь
def make_dict(text):
    f = []
    for line in text:
        line = line.split()
        for word in line:
            word = word.strip()
            f.append(word.strip())
    text = collections.Counter(f)
    return text

#Из словаря выбираем случайное слово с частотностью > 3
def randomizer(text):
    f = []
    for keys,value in text.items():
        if value >= 3:
            f.append(keys)
    return random.choice(f)

def main():
    text = opener('1stsem.txt')
    text = make_dict(text)
    text = randomizer(text)
    print(text)
        
main()