def _start():
  func(100) # -> int function!!!
  func(1.0) # -> float function!!!

def func(i: SystemInt32) -> SystemVoid:
  UnityEngineDebug.Log(SystemObject('int function!!!')) 

def func(s: SystemSingle) -> SystemVoid:
  UnityEngineDebug.Log(SystemObject('float function!!!')) 
