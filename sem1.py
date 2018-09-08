import collections
import random

def opener(filename):
    with open(filename, 'r', encoding="utf-8") as f:
    text = f.readlines()
    return text

def make_dict(text):
    f = []
    for line in text:
        line = line.split()
        for word in line:
            word = word.strip()
            f.append(word.strip())
    text = collections.Counter(f)
    return text

def randomizer(text):
    f = []
    for keys,value in text.items():
        if value >= 3:
            f.append(keys)
    return random.choice(f)

def main():
    text = opener('sem1.py')
    text = make_dict(text)
    text = randomizer()
        
main()

