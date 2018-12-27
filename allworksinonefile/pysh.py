import os

path = os.path.join(os.getcwd(), 'plain', '2018', '12', '9')
path_1 = path.replace('plain', 'mystem-plain')
path_2 = path.replace('plain', 'mystem-xml')


def stemmer(path, path_1, path_2):
    if not os.path.exists(path_1):
        os.makedirs(path_1)
    if not os.path.exists(path_2):
        os.makedirs(path_2)
    inp = os.listdir(path)
    for fl in inp:
        os.system(r'C:\mystem.exe -lcid --eng-gr ' + path + os.sep + fl + ' ' + path_1 + os.sep + fl)
        os.system(r'C:\mystem.exe -lcid --eng-gr --format xml ' + path + os.sep + fl + ' '+ path_2 + os.sep + fl)

stemmer(path, path_1, path_2)