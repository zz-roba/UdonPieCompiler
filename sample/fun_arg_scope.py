from .UdonPie import *  # IGNORE_LINE


def _start():
    a = 5
    b = 7
    c = add(a, b)
    Debug.Log(Object("add result: " + Convert.ToString(c))) # 12
    Debug.Log(Object("a = " + Convert.ToString(a))) # 5
    Debug.Log(Object("b = " + Convert.ToString(b))) # 7
    var_test(a, b)
    Debug.Log(Object("a = " + Convert.ToString(a))) # 5
    Debug.Log(Object("b = " + Convert.ToString(b))) # 7

def add(a: Int32, b: Int32) -> Int32:
    return a + b

def var_test(a: Int32, b:Int32) -> Void:
    a = 10000
    b = 20000
    Debug.Log(Object("a = " + Convert.ToString(a))) # 10000
    Debug.Log(Object("b = " + Convert.ToString(b))) # 20000
