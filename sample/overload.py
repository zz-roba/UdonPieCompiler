from .UdonPie import *  # IGNORE_LINE


def _start():
    func(100)  # -> int function!!!
    func(1.0)  # -> float function!!!


def func(i: Int32) -> Void:
    Debug.Log(Object('int function!!!'))


def func(s: Single) -> Void:
    Debug.Log(Object('float function!!!'))
