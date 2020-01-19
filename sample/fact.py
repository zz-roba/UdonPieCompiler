# IT DOES NOT WORK!
def fact(x: SystemInt32) -> SystemInt32:
  if x <= 0:
    return 1
  else:
    return fact(x - 1) * x

def _start():
  UnityEngineDebug.Log(SystemObject(fact(5)))

