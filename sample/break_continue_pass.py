def _start():
  # break
  UnityEngineDebug.Log(SystemObject("break test")) 
  i = 1
  while True:
    UnityEngineDebug.Log(SystemObject("count :" + SystemConvert.ToString(i))) 
    if 10000 < i:
      break
    i *= 2

  # continue
  UnityEngineDebug.Log(SystemObject("continue test")) 
  i = 0
  while i < 10:
    i += 1
    if i % 3 == 0:
      continue
    UnityEngineDebug.Log(SystemObject("count :" + SystemConvert.ToString(i))) 
  
  # pass
  if True:
    pass
