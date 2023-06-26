from typing import List


class Obj:
    pass


data = [Obj(), Obj(), Obj()]


def fun(li: List[Obj]):
    obb = li[1]
    li.remove(obb)


fun(data)

print(len(data))
