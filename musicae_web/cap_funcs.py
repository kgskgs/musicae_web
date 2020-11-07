import random
from operator import __add__, __sub__
#import inspect


class add_sub_challange():

    def __init__(self):
        self.ranges = {
            (1, __add__): (0, 8),
            (1, __sub__): (1, 9),
            (2, __add__): (0, 7),
            (2, __sub__): (2, 9),
            (3, __add__): (0, 6),
            (3, __sub__): (3, 9),
        }

        self.reroll()

    def __call__(self):
        #curframe = inspect.currentframe()
        #calframe = inspect.getouterframes(curframe, 2)
        #print(calframe)

        lo, hi = self.ranges[(self.mod, self.op)]
        ret = u''
        res = u''

        print(f"challange class: {self.mod} {self.op}")

        for i in range(4):
            digit = random.randint(lo, hi)
            ret += str(digit)
            res += str(self.op(digit, self.mod))

        self.reroll()

        return ret, res

    def reroll(self):
        self.mod = random.choice([1, 2, 3])
        self.op = random.choice([__add__, __sub__])
