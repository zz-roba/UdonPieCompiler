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
* Static typing (UdonPie differs from Python in that all variable types are determined at compile time.)
* Operators (
  `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^`, `>>`, `<<`,
  `==`, `!=`, `<`, `>`, `<=`, `>=`,
  `and`, `or`, `not`)
* `if` / `while` / `return` / `break` / `continue`  statments
* Assing statments(`+=`, `-=` `*=`, `/=`, `&=`, `|=`, `^=`, `>>=`, `<<=`)
* Udon Extern API call
* User-defined function
  (Still, functions cannot be recursive.)
* Simple type inference / checking
* Force cast
* Function overload
* The `this_trans` keyword represents this.UnityEngineTransform object for that object
* The `this_gameObj` keyword represents this.UnityEngineGameObject object for that object
* Built-in function `instantiate`
* Udon Extern completion\
  Code completion is realized by
   "Python class file provided by [@Grim_es](https://twitter.com/Grim_es)" 
   and "Editor with code completion function".\
   The usage is described below.
   (`How to use Udon Extern completion`)
* Array subscript access
 
## Requirement
* Python 3.6.8
* VRCSDK3 (Testing with VRCSDK3-2020.02.03.22.36.unitypackage)
* UDONSDK (Testing with UDONSDK-2020.02.03.11.56_Public.unitypackage)
* `pip install -r requirements.txt`

## Roadmap
* Implement user-defined recursive function
* Implement Event with argument
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
        if i % 3 == 0 and i % 5 == 0:
            Debug.Log(Object('fizzbuzz.'))
        elif i % 3 == 0:
            Debug.Log(Object('fizz.'))
        elif i % 5 == 0:
            Debug.Log(Object('buzz.'))
        else:
            Debug.Log(Object(i))
        i += 1
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
def func1(x_1: Int32, y_1: Int32) -> Int32:
    return 2 * x_1 + y_1


def func2(x_2: Int32, y_2: Int32) -> Int32:
    return x_2 / y_2


def print_calc() -> Void:
    a = func1(100, 1000) # 1200
    b = func2(a, 10) # 120
    # If the types do not match,
    # a function call or operation will result in an error.
    Debug.Log(Object(b)) # output 120


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
    cube = GameObject.Find('Cube')
    # An array is realized by the method of the {TypeName} Array class. (Not implemented at language level)
    # Make 10x10 size GameObjectArray Object
    cubes = GameObjectArray.ctor(10 * 10)
    y_i = 0
    while y_i < 10:
        x_i = 0
        while x_i < 10:
            # duplicate
            cube_obj = instantiate(cube)
            # setting
            cube_insta = Transform(cube_obj.GetComponent('Transform'))
            # Cannot do implicit cast
            tmp_x = Convert.ToSingle(x_i)
            tmp_y = Convert.ToSingle(y_i)
            cube_insta.set_position(
                Vector3.ctor(tmp_x, 0.0, tmp_y)
            )
            cubes[10 * y_i + x_i] = cube_obj
            x_i = x_i + 1
        y_i = y_i + 1


# MouseDown　Event
def _onMouseDown():
    cube_i = 0
    while cube_i < 10 * 10:
        # Color change randomly
        cube_renda = Renderer(cubes[cube_i].GetComponent('Renderer'))
        cube_renda.get_material().set_color(Random.ColorHSV())
        cube_i = cube_i + 1
```
```py
# OnPlayerJoined Event
def _onPlayerJoined(playerApi: VRCPlayerApi):
    Debug.Log(Object(playerApi))
```


## How to use Udon Extern completion
* Extract the `UdonPie.zip` or` tools / UdonPie.zip` file.
* Put the `UdonPie` directory in the same directory as the UdonPie source code.
* Put `from. UdonPie import * # IGNORE_LINE` at the top of UdonPie source code.  \
  (The UdonPie compiler ignores `Import` and` From`, which are used as input completion hints in the editor.)
* Open the UdonPie source code in an input-completion editor such as PyCharm or VSCode.


## UdonPie Usefull Links
### [Getting Started with UdonPie - the Python-based UDON-assembly compiler](https://ask.vrchat.com/t/getting-started-with-udonpie-the-python-based-udon-assembly-compiler/384)
Guide to getting started with UdonPie

### [Pile o' Pies](https://www.notion.so/Pile-o-Pies-3cab00c83ff44bb080821fa4e1cade43)
A collection of small UdonPie-based UDON programs

### [Udon Extern Search](https://7colou.red/UdonExternSearch/)

Service to search Udon Extern API

## Similar projects

### [cannorin / SAnuki Intermediate Language for Udon](https://github.com/cannorin/sanuki)
Intermediate Language for Udon Assembly

### [Doshik language custom compiler](https://ask.vrchat.com/t/doshik-language-custom-compiler/369)

## Thanks

### cannorin / UdonTest
https://github.com/cannorin/UdonTest
* I used this project in order to make UdonAPI table `udon_funcs_data.py`.

### [@Grim_es](https://twitter.com/Grim_es)
* He created a `UdonPie` file that implements Udon extern completion.

### [@Foorack](https://twitter.com/Foorack)
* He has added 
  * Array subscript.
  * binary operators(`&`, `|`, `^`, `>>`, `<<`)
  * Augmented assignment statements(`+=`, `-=` `*=`, `/=`, `&=`, `|=`, `^=`, `>>=`, `<<=`)
* And, so many fixes

### Chiel Douwes (https://github.com/chieltbest)
* He fixed the reference processing of resource_path.

### [@orels1_](https://twitter.com/orels1_)
*  He has created a detailed UdonPie guide. \
[Getting Started with UdonPie - the Python-based UDON-assembly compiler](https://ask.vrchat.com/t/getting-started-with-udonpie-the-python-based-udon-assembly-compiler/384/3)
* He has created many UdonPie code examples. \
[Pile o' Pies](https://www.notion.so/Pile-o-Pies-3cab00c83ff44bb080821fa4e1cade43)

### cannorin / UdonExternSearch
https://github.com/cannorin/UdonExternSearch
* This is useful for finding UdonAPI functions.

## How to Make exe file
```
pip install -r requirements.txt
make_exe.bat
(The exe file is generated in "dist / UdonPie.exe".)
```

## Author

[zz_roba](https://github.com/tcnksm)

