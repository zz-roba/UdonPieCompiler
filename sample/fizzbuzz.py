# fizzbuzz
def _start():
  i = 1
  # Control Statments are only If and While
  while i <= 100:
    # Logical operators ("and" and "or") cannot be written consecutively
    # ("A and B and C" must be written as "(A and B) and C").
    if i % 3 == 0 and i % 5 == 5:
      UnityEngineDebug.Log(SystemObject('fizzbuzz.'))
    elif i % 3 == 0:
      UnityEngineDebug.Log(SystemObject('fizz.'))
    elif i % 5 == 0:
      UnityEngineDebug.Log(SystemObject('buzz.'))
    else:
      UnityEngineDebug.Log(SystemObject(i))
    i += 1
