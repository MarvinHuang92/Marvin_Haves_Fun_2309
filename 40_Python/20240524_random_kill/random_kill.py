"""
随机杀人游戏
编号1-50, 每次随机杀一个奇数号的人
后面号码的人依次向前递进
直到最后一人
计算各个初始号码的存活概率
"""

import random

class Person():
    def __init__(self, init_number):
        self.init_number = init_number
        self.current_number = init_number
        self.state = 'alive'
    
    def is_killed(self):
        self.state = 'dead'
    
    def is_alive(self):
        return self.state == 'alive'
    
    def is_odd(self):
        return self.current_number % 2 == 1
    
    def set_number(self, number):
        self.current_number = number

class Array():
    def __init__(self, max_number):
        self.array = []
        for i in range(max_number):
            self.array.append(Person(i+1))
    
    def kill(self):
        temp_list = []
        for person in self.array:
            if person.is_odd():
                temp_list.append(person)
        i = random.randint(1, len(temp_list))
        killed_person = self.array.pop(2*(i-1))
        # print("Person_%02d is killed, current order: %02d" % (killed_person.init_number, killed_person.current_number))
    
    def reorder(self):
        num = 1
        for person in self.array:
            person.set_number(num)
            num += 1

def game(max_number):

    a = Array(max_number)

    for i in range(max_number - 1):
        a.kill()
        a.reorder()

    ret = a.array[0].init_number
    # print("Person_%02d is Last survivor!" % ret)

    return ret


if __name__ =="__main__":

    max_number = 50
    game_round = 100000

    ret_list = []
    for i in range(game_round):
        ret_list.append(game(max_number))

    for line in ret_list:
        print(line)