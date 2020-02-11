def _start():
  a = 5
  b = 7
  c = add(a, b)
  UnityEngineDebug.Log(SystemObject("add result: " + SystemConvert.ToString(c))) # 12
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a))) # 5
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(b))) # 7
  var_test(a, b)
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a))) # 5
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(b))) # 7

def add(a: SystemInt32, b: SystemInt32) -> SystemInt32:
  return a + b

def var_test(a: SystemInt32, b:SystemInt32) -> SystemVoid:
  a = 10000
  b = 20000
  UnityEngineDebug.Log(SystemObject("a = " + SystemConvert.ToString(a))) # 10000
  UnityEngineDebug.Log(SystemObject("b = " + SystemConvert.ToString(b))) # 20000
