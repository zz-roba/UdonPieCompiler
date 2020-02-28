from .UdonPie import *  # IGNORE_LINE


# fizzbuzz
def _start():
    i = 1
    # Control Statments are only If and While
    while i <= 100:
        # Logical operators ("and" and "or") cannot be written consecutively
        # ("A and B and C" must be written as "(A and B) and C").
        if i % 3 == 0 and i % 5 == 0:
            Debug.Log(Object('fizzbuzz.'))
        elif i % 3 == 0:
            Debug.Log(Object('fizz.'))
        elif i % 5 == 0:
            Debug.Log(Object('buzz.'))
        else:
            Debug.Log(Object(i))
        i += 1
