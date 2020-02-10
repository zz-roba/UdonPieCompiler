def _start():
  a = 5
  b = 7
  c = add(a, b)
  UnityEngineDebug.Log(SystemObject("Result: " + SystemConvert.ToString(c)))

def add(a: SystemInt32, b: SystemInt32) -> SystemInt32:
  return a + b
