from .UdonPie import *  # IGNORE_LINE


# IT DOES NOT WORK!
def fact(x: Int32) -> Int32:
    if x <= 0:
        return 1
    else:
        return fact(x - 1) * x


def _start():
    Debug.Log(Object(fact(5)))
