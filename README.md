UdonPie Compiler
====

* UdonPie is a language similar to Python.\
(The parser part is Python 3.6. But semantic analysis is different from Python)
* UdonPie compiler translates UdonPie code into Udon Assembly.
* ** If you find a English mistake, it will help. **
* Project Page: https://github.com/zz-roba/UdonPieCompiler

## Download Exe File
https://zz-roba.booth.pm/items/1789601


## Features
* Operators(only `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `and`, `or`, `not`)
* `If` / `While` / `return` Statments
* Udon Extern API call
* User-defined function
  (Still, functions cannot be recursive.)
* Simple type inference / checking
* Force cast
* The `this_trans` keyword represents this.UnityEngineTransform object for that object
* The `this_gameObj` keyword represents this.UnityEngineGameObject object for that object
* Built-in function `instantiate`


## Requirement
* Python 3.6.8
* VRCSDK3 (Testing with VRCSDK3-2020.01.14.10.40.unitypackage)
* UDONSDK (Testing with UDONSDK-2020.01.14.10.47_Public.unitypackage)
* `pip install -r requirements.txt`

## Roadmap
* Implement user-defined recursive function
* Implement Inline Udon Assembler
* Implement Impliment Udon Optimisation
* Implement Udon Decompiler

## Usage
```
usage: udon_compiler.py [-h] input output (python code)
    or UdonPieC.exe [-h] input output (exe file)

positional arguments:
  input       input UdonPie source code path (ex: .\example.py)
  output      output Udon Assembly code path (ex: .\example.uasm)

optional arguments:
  -h, --help  show this help message and exit
```

## Sample code
``` py
# fizzbuzz
def _start():
  i = 1
  # Control Statments are only If and While
  while i <= 100:
    # Logical operators ("and" and "or") cannot be written consecutively
    # ("A and B and C" must be written as "(A and B) and C").
    if i == i / 3 * 3 and i == i / 5 * 5:
      UnityEngineDebug.Log(SystemObject('fizzbuzz.'))
    elif i == i / 3 * 3:
      UnityEngineDebug.Log(SystemObject('fizz.'))
    elif i == i / 5 * 5:
      UnityEngineDebug.Log(SystemObject('buzz.'))
    else:
      UnityEngineDebug.Log(SystemObject(i))
    i = i + 1
```


```py
# You can make the variable var_name global
# by typing "global {var_name}" at the beginning of the code.
global a
global b

# Variable declaration is performed in the following cases.
# * When assigned for the first time
# * At the time of variable declaration of argument
# The scope of all variables is the entire source code.

# You must always specify the types of function arguments and return values.
def func1(x_1: SystemInt32, y_1: SystemInt32) -> SystemInt32:
  return 2 * x_1 + y_1

def func2(x_2: SystemInt32, y_2: SystemInt32) -> SystemInt32:
  return x_2 / y_2

def print_calc() -> SystemVoid:
  a = func1(100, 1000) # 1200
  b = func2(a, 10) # 120
  # If the types do not match,
  # a function call or operation will result in an error.
  UnityEngineDebug.Log(SystemObject(b)) # output 120

# Event declarations begin with _.
def _start():
  print_calc()
```

``` py
# Place randomly colored blocks in the scene
# Demo Video https://twitter.com/zz_roba/status/1213365214135013376
# Start Event
def _start():
  # Cube to duplicate
  cube = UnityEngineGameObject.Find('Cube')
  # An array is realized by the method of the {TypeName} Array class. (Not implemented at language level)
  # Make 10x10 size GameObjectArray Object
  cubes = UnityEngineGameObjectArray.ctor(10 * 10)
  y_i = 0
  while y_i < 10:
    x_i = 0
    while x_i < 10:
      # duplicate
      cube_obj = instantiate(cube)
      # setting
      cube_insta = UnityEngineTransform(cube_obj.GetComponent('Transform'))
      # Cannot do implicit cast
      tmp_x = SystemConvert.ToSingle(x_i)
      tmp_y = SystemConvert.ToSingle(y_i)
      cube_insta.set_position(
        UnityEngineVector3.ctor(tmp_x, 0.0, tmp_y)
      )
      cubes[10 * y_i + x_i] = cube_obj
      x_i = x_i + 1
    y_i = y_i + 1 

# MouseDown　Event
def _onMouseDown():
  cube_i = 0
  while cube_i < 10 * 10:
    # Color change randomly
    cube_renda = UnityEngineRenderer(cubes[cube_i].GetComponent('Renderer'))
    cube_renda.get_material().set_color(UnityEngineRandom.ColorHSV())
    cube_i = cube_i + 1 

```


## Similar projects

### cannorin / SAnuki Intermediate Language for Udon
https://github.com/cannorin/sanuki

## Thanks
### cannorin / UdonTest
https://github.com/cannorin/UdonTest
* I used this project in order to make UdonAPI table `udon_funcs_data.py`.


## How to Make exe file
```
pip install -r requirements.txt
make_exe.bat
(The exe file is generated in "dist / UdonPie.exe".)
```

## Author

[zz_roba](https://github.com/tcnksm)

