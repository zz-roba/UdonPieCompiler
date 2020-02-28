from .UdonPie import *  # IGNORE_LINE


def _start():
    # break
    Debug.Log(Object("break test"))
    i = 1
    while True:
        Debug.Log(Object("count :" + Convert.ToString(i)))
        if 10000 < i:
            break
        i *= 2

    # continue
    Debug.Log(Object("continue test"))
    i = 0
    while i < 10:
        i += 1
        if i % 3 == 0:
            continue
        Debug.Log(Object("count :" + Convert.ToString(i)))

        # pass
    if True:
        pass
