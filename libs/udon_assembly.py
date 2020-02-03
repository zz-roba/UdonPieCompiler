import sys
import ast
# Commented out because Pyinstaller failed to run.
# import astor # type: ignore
import re
import pprint as pp
from typing import *
from typing_extensions import Literal # 3.8: typing.Literal
from .my_type import *
from .tables import *
from libs.udon_types import *
from libs.event_data import *

# python 3.6.8

class UdonAssembly:
  asm: str
  pc: Addr
  id_counter: int
  label_dict: Dict[LabelName, Addr]
  event_names: List[EventName]
  export_vars: List[VarName]
  var_table: VarTable
  def_func_table: DefFuncTable
  udon_method_table: UdonMethodTable
  env_vars: List[VarName]

  def __init__(self, var_table: VarTable, def_func_table: DefFuncTable) -> None:
    self.asm = ''
    self.pc = Addr(0)
    self.ld_counter = 0
    self.label_dict = {}
    self.event_names = []
    self.export_vars = []
    self.var_table = var_table
    self.def_func_table = def_func_table
    self.udon_method_table = UdonMethodTable()
    self.env_vars = []

  def add_inst_comment(self, comment: str) -> None:
    # self.asm += f'        # {comment}\n'
    return

  def add_inst(self, bcode_size: Addr, inst: str) -> None:
    self.asm += f'        {inst}\n'
    self.pc = Addr(self.pc + bcode_size)

  def make_code_seg(self) -> str:
    ret_code: str = f'.code_start\n\n'
    for event_name in self.event_names:
      ret_code += f'    .export {event_name}\n'
    ret_code += f'{self.asm}\n'
    ret_code += f'.code_end\n'
    return ret_code

  def get_next_id(self, name: str) -> str:
    ret_id = f'__{name}_{self.ld_counter}'
    self.ld_counter += 1
    return ret_id

  def add_label_crrent_addr(self, label: LabelName) -> None:
    self.label_dict[label] = self.pc

  ######################
  # Udon Instructions And Wrapper

  def nop(self):
    self.add_inst(1, 'NOP')

  def remove_top(self):
    'Udon POP is removing top'
    self.add_inst_comment('Remove Top')
    self.add_inst(1, 'POP')
  
  def pop_var(self, ret_value_name: VarName) -> None:
    'True POP'
    self.add_inst_comment(f'Pop(Push->Copy) {ret_value_name}')
    ret_type: Optional[UdonTypeName] = self.var_table.get_var_type(ret_value_name)
    if ret_type is None:
      raise Exception(f'pop: Variable {ret_value_name} is not defined.')
    # self.var_table.add_var(ret_value_name, ret_type, 'null')
    self.push_var(ret_value_name)
    self.copy()

  def pop_vars(self, var_names: List[VarName]) -> None:
    self.add_inst_comment(f'Pops {str(var_names)}')
    for var_name in reversed(var_names):
      self.pop_var(var_name)

  def push(self, addr: Addr) -> None:
    self.add_inst(Addr(5), f'PUSH, {addr:010x}')

  def push_var(self, var_name: VarName) -> None:
    self.add_inst(Addr(5), f'PUSH, {var_name}')

  def push_vars(self, var_names: List[VarName]) -> None:
    self.add_inst_comment(f'Pushs {str(var_names)}')
    for var_name in var_names:
      self.push_var(var_name)

  def copy(self) -> None:
    self.add_inst(Addr(1), 'COPY')
    
  def push_str(self, _str: str) -> None:
    self.add_inst(Addr(5), f'PUSH, "{_str}"')

  def jump(self, addr: Addr) -> None:
    self.add_inst(Addr(5), f'JUMP, 0x{addr:010x}')

  def jump_label(self, label: LabelName) -> None:
    # ###{label}### is temporary label
    self.add_inst(Addr(5), f'JUMP, ###{label}###')

  def jump_if_false(self, addr: Addr) -> None:
    self.add_inst(Addr(5), f'JUMP_IF_FALSE, 0x{addr:010x}')

  def jump_if_false_label(self, label: LabelName) -> None:
    # ###{label}### is temporary label
    self.add_inst(Addr(5), f'JUMP_IF_FALSE, ###{label}###')

  def jump_indirect(self, var_name: VarName) -> None:
    self.add_inst(Addr(5), f'JUMP_INDIRECT, {var_name}')

  def jump_ret_addr(self) -> None:
    self.add_inst(Addr(5), f'JUMP_INDIRECT, ret_addr')

  def extern(self, extern_str: ExternStr) -> None:
    self.add_inst(Addr(5), f'EXTERN, "{extern_str}"')

  def end(self) -> None:
    """event end"""
    self.add_inst(Addr(5), f'JUMP, 0xFFFFFF')
    return

  def call_extern(self, extern_str: ExternStr, arg_vars: List[VarName]) -> None:
    """
       src0, src1, .. dist
    """
    
    self.add_inst_comment(f'Call Extern {str(extern_str)}{str(arg_vars)}')
    arg_var: VarName
    for arg_var in arg_vars:
      self.push_var(arg_var)
    self.extern(extern_str)

  def assign(self, dist_var_name: VarName, src_var_name: VarName) -> None:
    "Add variable, "
    # If the variable name on the right side is UdonTypeName, 
    # just set the type of the variable on the left.
    src_var_type: UdonTypeName
    if src_var_name in udon_types:
        src_var_type = UdonTypeName(src_var_name)
        self.var_table.add_var(dist_var_name, src_var_type, 'null')
    else:
      src_var_type = self.var_table.get_var_type(src_var_name)
      # If the left variable is undefined, define the variable.
      if not self.var_table.exist_var(dist_var_name):
        self.add_inst_comment(f'Declare {dist_var_name}')
        self.var_table.add_var(dist_var_name, src_var_type, 'null')
      self.add_inst_comment(f'{str(dist_var_name)} = {str(src_var_name)}')
      self.push_var(src_var_name)
      self.push_var(dist_var_name)
      self.copy()

  def set_bool(self, var_name: VarName, bool_num: bool) -> None:
    self.push_str(f"{'true' if bool_num else 'false'}")
    self.push_var(var_name)
    self.extern(ExternStr('SystemBoolean.__Parse__SystemString__SystemBoolean'))

  def set_uint32(self, var_name: VarName, num: int) -> None:
    self.add_inst_comment(f'{str(var_name)} = {str(num)}')
    const_var_name = VarName(self.get_next_id('const_uint32'))
    self.var_table.add_var(const_var_name, UdonTypeName('SystemUInt32'), f'{num}')
    self.push_var(const_var_name)
    self.push_var(var_name)
    self.copy()

  def get_addr(self, label: LabelName) -> Addr:
    """ get address from  temporary label"""
    return self.label_dict[label]

  def add_label(self, label: LabelName, addr: Addr) -> None:
    self.label_dict[label] = addr
  
  # BAD METHOD
  def replace_tmp_adrr(self, code: str) -> str:
    replace_str: str = ''
    for line in code.split('\n'):
        match = re.match(r'.*###(.*)###.*', line)
        if match is not None and match.group(1) is not None:
            label_name = LabelName(match.group(1))
            line_new = line.replace(f'###{label_name}###', f'0x{self.get_addr(label_name):010x}')
            replace_str += f'{line_new}\n'
        else:
            replace_str += f'{line}\n'
    return replace_str
  
  def call_def_func(self, func_name: FuncName, arg_var_names: List[VarName]) -> Optional[VarName]:
    self.add_inst_comment(f'Call DefFunc {str(func_name)}{str(arg_var_names)}')
    arg_var_types: List[UdonTypeName] = [
      self.var_table.get_var_type(arg_var_name) for arg_var_name in arg_var_names]
    ret_type_name: UdonTypeName = self.def_func_table.get_ret_type(func_name, tuple(arg_var_types))
    ret_call_label = LabelName(self.get_next_id('ret_call_label'))
    const_ret_addr = VarName(self.get_next_id('const_ret_addr'))
    ret_value = VarName(self.get_next_id('ret_value'))
    # Save current return address
    self.push_var(VarName('ret_addr'))
    # Save environment variables
    self.push_vars(self.env_vars)
    # Save return address in order to return
    self.var_table.add_var(
      VarName(const_ret_addr),
      UdonTypeName('SystemUInt32'),
      f'###{ret_call_label}###')
    # self.assign(VarName('ret_addr'), VarName(const_ret_addr))
    self.push_var(VarName(const_ret_addr))
    # Push arguments
    self.push_vars(arg_var_names)
    # goto func label
    self.jump_label(LabelName(func_name))
    self.add_label_crrent_addr(ret_call_label)

    if ret_type_name != UdonTypeName('SystemVoid'):
      # pop ret_var_name
      self.var_table.add_var(ret_value, ret_type_name, 'null')
      self.pop_var(ret_value)
      # restore environment
      self.pop_vars(self.env_vars)
      # restore current return address
      self.pop_var(VarName('ret_addr'))
      return ret_value
    else:
      # restore environment
      self.pop_vars(self.env_vars)
      # restore current return address
      self.pop_var(VarName('ret_addr'))
      return None

  def add_event(self, event_name: EventName,
                def_arg_var_names: List[VarName], def_arg_types: List[UdonTypeName]) -> None:
    if event_name in event_table:
      table_arg_type_and_names = event_table[event_name]
      # Define the variables required for the event with arguments.
      pair_var_names_var_types =  zip(table_arg_type_and_names, def_arg_var_names, def_arg_types)

      if len(table_arg_type_and_names) != len(def_arg_var_names):
          raise Exception(f'add_event: The required arguments for event {event_name} and the number of defined arguments are different.')

      for ((table_arg_type_name, table_arg_name), def_arg_var_name, def_arg_type) in pair_var_names_var_types:
        if table_arg_type_name != def_arg_type:
          raise Exception(f'add_event: The type of the argument of event {event_name} is different.')
        self.var_table.add_var(VarName(table_arg_name), UdonTypeName(table_arg_type_name), 'null')
    else:
      # TODO: Add user event processing
      # (I still don't understand the specifications of user events)
      table_arg_type_and_names = ()
    
    self.event_names.append(event_name)

  def event_head(self, event_name: EventName) -> None:
    self.asm += f'    {event_name}:\n'

if __name__ == "__main__":
  pass