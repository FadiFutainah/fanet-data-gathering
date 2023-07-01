from copy import deepcopy
from typing import List


class Obj:
    def __init__(self):
        self.cnt = 1

    def pp(self):
        self.cnt += 1


data = [Obj(), Obj(), Obj()]

data2 = deepcopy(data)


def fun(li: List[Obj]):
    obb = li[1]
    li.remove(obb)

# fun(data)

# print(data)
# print(data2)
