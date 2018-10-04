#Задание №1


def opener(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        a = f.read()
    return a


def main1():
    print('Задание №1')
    a = opener('bagr.txt')
    b = opener('mayak.txt')
    a = set(a.split()) #делаем множество из первого стиха
    b = set(b.split()) #делаем множество из второго стиха
    print(a & b) #пересечение
    print(a ^ b) #симметрическая разность

main1()

#Задание №2


def task2(name, phone):
    if name not in phone:
        print('Этого имени в телефонной книге нет')
        phone[name] = phone.get(name, int(input('Введите телефонный номер данного абонента: ')))
    else:
        phone[name] = phone.get(name)
    return phone[name]


def main2():
    print("Задание №2")
    d = {}
    name = input('Введите имя: ')
    phone = task2(name, d)
    print(phone)

main2()
