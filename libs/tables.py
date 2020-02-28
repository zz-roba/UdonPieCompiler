# python 3.6.8
import sys
import os
import ast
# Commented out because Pyinstaller failed to run.
# import astor # type: ignore
import re
import pprint as pp
from typing import *
from typing_extensions import Literal # 3.8: typing.Literal
from .my_type import *
from libs.udon_types import *


def resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path) # type: ignore
    return os.path.join(os.path.dirname(__file__), "..", relative_path)

class VarTable:
  """
  Variable Table
  """
  var_dict: Dict[VarName, Tuple[UdonTypeName, str]]
  global_var_names: List[VarName]
  current_func_id: Optional[LabelName]

  def __init__(self) -> None:
    self.var_dict = {}
    self.global_var_names = []
    self.current_func_id = None

  def resolve_varname(self, var_name: VarName) -> VarName:
    tmp_varname = VarName(f'{self.current_func_id}_{var_name}')
    if (self.current_func_id is not None) and (tmp_varname in self.var_dict):
      return tmp_varname
    else:
      return var_name

  def add_var(self, var_name: VarName, type_name: UdonTypeName, init_value_str: str) -> None:
    if var_name in self.var_dict:
      raise Exception(f'add_var: {var_name} is already registered.')
    if type_name == UdonTypeName('Void'):
      raise Exception(f'add_var: {var_name} is Void.')
    # print(f'add_var({var_name}, {type_name}, {init_value_str})')
    self.var_dict[var_name] = (type_name, init_value_str)


  def get_var_type(self, var_name: VarName) -> UdonTypeName:
    if not self.exist_var(var_name):
      if var_name in udon_types:
        return UdonTypeName(var_name)
      else:
        raise Exception(f'get_var_type: Variable {var_name} is not defined.')
    ret_type: UdonTypeName
    ret_type, _ = self.var_dict[var_name]
    return ret_type

  def valid_var_type(self, var_name: VarName, assert_var_type: UdonTypeName) -> ValidStatus:
    if not self.exist_var(var_name):
      return 'NOT_EXIST'
    ret_type: UdonTypeName
    type_name, _ = self.var_dict[var_name]
    if assert_var_type == type_name:
      return 'VALID'
    return 'NOT_VALID'
  
  def exist_var(self, var_name: VarName) -> bool:
    return var_name in self.var_dict
  
  def make_data_seg(self) -> str:
    """making .data segment str"""
    data_str: str = '.data_start\n\n'
    for var_name in self.global_var_names:
      if not self.exist_var(var_name):
        raise Exception(f'make_data_seg: Global variable {var_name} is not defined.')
      data_str += f'    .export {var_name}\n'
    for (var_name, (type_name, init_value)) in self.var_dict.items():
      # There is no class with the name VRCUdonUdonBehaviour, but UdonVM requires it to be named like that anyway.
      if type_name == "VRCUdonCommonInterfacesIUdonEventReceiver":
        data_str += f'        {var_name}: %VRCUdonUdonBehaviour, {init_value}\n'
      else:
        data_str += f'        {var_name}: %{udon_types[type_name]}, {init_value}\n'
    data_str += f'\n.data_end\n\n'
    return data_str

  def print_data_seg(self) -> None:
    print(self.make_data_seg())

class DefFuncTable:
  """
  Function Table
  """
  func_dict: Dict[
    Tuple[FuncName, Tuple[UdonTypeName, ...]],
    Tuple[UdonTypeName, Tuple[VarName, ...]]
  ]

  def __init__(self) -> None:
    self.func_dict = {}

  def add_func(self, func_name: FuncName, arg_types: Tuple[UdonTypeName, ...],
               ret_type: UdonTypeName, arg_names: Tuple[VarName, ...]) -> None:
    self.func_dict[(func_name, arg_types)] = (ret_type, arg_names)

  def exist_func(self, func_name: FuncName, arg_types: Tuple[UdonTypeName, ...]) -> bool:
    return (func_name, arg_types) in self.func_dict

  def get_ret_type(self, func_name: FuncName, arg_types: Tuple[UdonTypeName, ...]) -> UdonTypeName:
    ret_type: UdonTypeName
    if not self.exist_func(func_name, arg_types):
      raise Exception(f'DefFuncTable.get_ret_type: Function {func_name}{arg_types} is not defined. \
Are the argument types correct?')
    ret_type, _ = self.func_dict[func_name, arg_types]
    return ret_type

  def get_function_id(self, func_name: FuncName, arg_types: List[UdonTypeName]) -> str:
    # ex) function id of func(:Int32, Float) is "func_SystemInt32_SystemFloat"
    return f'{func_name}__{"_".join(arg_types)}'


class UdonMethodTable:
  udon_method_dict: Dict[
    # (method_kind, udon_module_type, (arg_type, ...))
    Tuple[UdonMethodKind, UdonTypeName, UdonMethodName, Tuple[UdonTypeName, ...]],
    # (ret_type, exturn_str)
    Tuple[UdonTypeName, ExternStr]
  ]

  def __init__(self) -> None:
    self.udon_method_dict = {}
    f = open(resource_path('udon_funcs_data.py'), encoding="utf-8")
    self.udon_method_dict = eval(f.read())

  def get_ret_type_extern_str(
                  self, method_kind: UdonMethodKind, udon_module_type: UdonTypeName,
                  method_name: UdonMethodName,
                  arg_types: Tuple[UdonTypeName, ...]) -> Optional[Tuple[UdonTypeName, ExternStr]]:
    key = (method_kind, udon_module_type, method_name, arg_types)
    if key in self.udon_method_dict:
      return self.udon_method_dict[key]
    else:
      return None


if __name__ == '__main__':
  var_table = VarTable()
  var_table.add_var(VarName('aaa'), UdonTypeName('Int32'), '100')
  var_table.add_var(VarName('bbb'), UdonTypeName('Int32'), '200')
  var_table.print_data_seg()

  udon_method_table = UdonMethodTable()
  # pp.pprint(udon_method_table.udon_method_dict)
  print(udon_method_table.get_ret_type_extern_str(
    'InstanceFunc',
    UdonTypeName('ByteArray'),
    UdonMethodName('GetValue'),
    (UdonTypeName('Int32'), )))
# ByteArray.GetValue Int32
