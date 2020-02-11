def _start():
  a = 5
  b = 7
  c = add(a, b)
  UnityEngineDebug.Log(SystemObject("add result: " + SystemConvert.ToString(c)))
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a)))
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(a)))
  var_test(a, b)
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a)))
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(a)))

def add(a: SystemInt32, b: SystemInt32) -> SystemInt32:
  return a + b

def var_test(a: SystemInt32, b:SystemInt32) -> SystemVoid:
  a = 10000
  b = 20000
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a)))
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(a)))
