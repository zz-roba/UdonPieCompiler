import sys
import ast
# Commented out because Pyinstaller failed to run.
# import astor # type: ignore
import re
import pprint as pp
import argparse
from typing import *
from typing_extensions import Literal # 3.8: typing.Literal
from libs.my_type import *
from libs.tables import *
from libs.udon_assembly import *
from libs.udon_types import *

# python 3.6.8

class UdonCompiler:
  var_table: VarTable
  uasm: UdonAssembly
  def_func_table: DefFuncTable
  udon_method_table: UdonMethodTable
  node: ast.AST

  def __init__(self, code: str) -> None:
    self.var_table = VarTable()
    self.def_func_table = DefFuncTable()
    self.uasm = UdonAssembly(self.var_table, self.def_func_table)
    self.udon_method_table = UdonMethodTable()
    self.node = ast.parse(code)

  def make_uasm_code(self) -> str:
    # return address
    self.var_table.add_var(VarName('ret_addr'), UdonTypeName('SystemUInt32'), '0xFFFFFF')
    # this
    self.var_table.add_var(VarName('this_trans'), UdonTypeName('UnityEngineTransform'), 'this')
    self.var_table.add_var(VarName('this_gameObj'), UdonTypeName('UnityEngineGameObject'), 'this')


    # parse and eval AST
    # FORCE CAST, NO CHECK
    node_body = cast(ast.Module, self.node)
    body: List[ast.stmt] = node_body.body
    self.pre_check_func_defs(body)
    self.eval_body(body)

    ret_code: str = ''
    ret_code += self.var_table.make_data_seg()
    ret_code += self.uasm.make_code_seg()
    ret_code = self.uasm.replace_tmp_adrr(ret_code)
    return ret_code

  def print_ast(self, node: ast.AST):
    # print(self.print_ast(node))
    return

  def pre_check_func_defs(self, body: List[ast.stmt]) -> None:
    stmt: ast.stmt
    for stmt in body:
      # Function definition
      # FunctionDef(identifier name, arguments args,
      #  stmt* body, expr* decorator_list, expr? returns,
      #  string? type_comment)
      if type(stmt) is ast.FunctionDef:
        # FORCE CAST
        funcdef_stmt: ast.FunctionDef = cast(ast.FunctionDef, stmt)
        func_name:str = funcdef_stmt.name
        # Functions starting with an underscore are events
        if func_name.startswith('_'):
          self.uasm.add_event(EventName(func_name))
        # Otherwise, the defined function
        else:
          arg_var_names: List[VarName]  = [VarName(arg.arg) for arg in funcdef_stmt.args.args]
          # FORCE CAST, NO CHECK
          arg_types: List[UdonTypeName] = [UdonTypeName(arg.annotation.id) for arg in funcdef_stmt.args.args]  # type: ignore
          ret_type: UdonTypeName
          # FORCE CAST, NO CHECK
          if funcdef_stmt.returns.id is not None: # type: ignore
            # FORCE CAST, NO CHECK
            ret_type = funcdef_stmt.returns.id  # type: ignore
          else:
            ret_type = UdonTypeName('SystemVoid')
          # Add to function table
          self.def_func_table.add_func(FuncName(func_name), tuple(arg_types), ret_type, tuple(arg_var_names))

  def eval_body(self, body: List[ast.stmt]) -> None:
    """
    Eval body(statments)
    """
    stmt: ast.stmt
    for stmt in body:
      # Global statment
      #  | Global(identifier* names)
      if type(stmt) is ast.Global:
        _global: ast.Global = cast(ast.Global, stmt)
        names = _global.names
        for name in names:
          self.var_table.global_var_names.append(VarName(name))
      # Assign statment
      #  | Assign(expr* targets, expr value)
      elif type(stmt) is ast.Assign:
        assign: ast.Assign = cast(ast.Assign, stmt)
        # right expression
        src_var_name: Optional[VarName] = self.eval_expr(assign.value)
        if src_var_name is None:
          raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: There is no value on the right side of the assignment statement.')
        # left expression
        # FORCE CAST, NO CHECK
        dist_var_name: VarName = assgin.targets[0].id # type: ignore
        self.uasm.assign(dist_var_name, src_var_name)

      # Expression
      # | Expr(expr value)
      elif type(stmt) is ast.Expr:
        expr: ast.Expr = cast(ast.Expr, stmt)
        self.eval_expr(expr.value)

      # If statment
      # | If(expr test, stmt* body, stmt* orelse)
      elif type(stmt) is ast.If:
        if_stmt: ast.If = cast(ast.If, stmt) # FORCE CAST
        else_label = LabelName(self.uasm.get_next_id('else_label'))
        if_end_label = LabelName(self.uasm.get_next_id('if_end_label'))

        test_result_var_name = self.eval_expr(if_stmt.test)
        if test_result_var_name is None:
          raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: There is no value for the conditional expression.')

        if self.var_table.get_var_type(test_result_var_name) != UdonTypeName('SystemBoolean'):
          raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: There is no value for the conditional expression.')
        self.uasm.push_var(test_result_var_name)
        # if (!test) goto else
        self.uasm.jump_if_false_label(else_label)
        # {}
        self.eval_body(if_stmt.body)
        # goto if_end
        self.uasm.jump_label(if_end_label)
        # else:
        self.uasm.add_label_crrent_addr(else_label)
        self.eval_body(if_stmt.orelse)
        # if_end:
        self.uasm.add_label_crrent_addr(if_end_label)

      # While statment
      # | While(expr test, stmt* body, stmt* orelse)
      # orelse is not implemented
      elif type(stmt) is ast.While:
        while_stmt: ast.While = cast(ast.While, stmt) # FORCE CAST
        while_label = LabelName(self.uasm.get_next_id('while_label'))
        while_end_label = LabelName(self.uasm.get_next_id('while_end_label'))
        # while_label:
        self.uasm.add_label_crrent_addr(while_label)
        test_result_var_name = self.eval_expr(while_stmt.test)
        if test_result_var_name is None:
          raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: There is no value for the conditional expression.')

        if self.var_table.get_var_type(test_result_var_name) != UdonTypeName('SystemBoolean'):
          raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: There is no value for the conditional expression.')
        self.uasm.push_var(test_result_var_name)
        # if (!test) goto else
        self.uasm.jump_if_false_label(while_end_label)
        # {}
        self.eval_body(while_stmt.body)
        # goto while:
        self.uasm.jump_label(while_label)
        # while_end:
        self.uasm.add_label_crrent_addr(while_end_label)

      # Function definition
      # FunctionDef(identifier name, arguments args,
      #  stmt* body, expr* decorator_list, expr? returns,
      #  string? type_comment)
      elif type(stmt) is ast.FunctionDef:
        # FORCE CAST
        funcdef_stmt: ast.FunctionDef = cast(ast.FunctionDef, stmt)
        func_name:str = funcdef_stmt.name
        # Functions starting with an underscore are events
        if func_name.startswith('_'):
          self.uasm.event_head(EventName(func_name))  # Move to pre_check_func_defs function
          # TODO: FIX
          self.uasm.set_uint32(VarName('ret_addr'), 0xFFFFFF)
          self.eval_body(funcdef_stmt.body)
          self.uasm.end()

        # Otherwise, the defined function
        else:
          self.uasm.add_label_crrent_addr(LabelName(func_name))
          arg_var_names: List[VarName]  = [VarName(arg.arg) for arg in funcdef_stmt.args.args]
          self.uasm.env_vars = arg_var_names 
          # FORCE CAST, NO CHECK
          arg_types: List[UdonTypeName] = [UdonTypeName(arg.annotation.id) for arg in funcdef_stmt.args.args]  # type: ignore
          # FORCE CAST, NO CHECK
          arg_var_name_types: List[Tuple[VarName, UdonTypeName]] = zip(arg_var_names, arg_types) # type: ignore
          ret_type: UdonTypeName
          # FORCE CAST, NO CHECK
          if funcdef_stmt.returns.id is not None: # type: ignore
            # FORCE CAST, NO CHECK
            ret_type = funcdef_stmt.returns.id  # type: ignore
          else:
            ret_type = UdonTypeName('SystemVoid')

          # Add argment tmp variables
          for arg_var_name, arg_type in arg_var_name_types:
            self.var_table.add_var(arg_var_name, arg_type, 'null')
          # Pop Argument
          self.uasm.pop_vars(arg_var_names)
          # Eval Function body
          self.eval_body(funcdef_stmt.body)
          # Pop Return Address
          self.uasm.pop_var(VarName('ret_addr'))
          # Return
          self.uasm.jump_ret_addr()
          self.uasm.env_vars = []

      # Return Statment
      # | Return(expr? value)
      elif type(stmt) is ast.Return:
        # FORCE CAST
        return_stmt: ast.Return = cast(ast.Return, stmt)
        # Pop Return Address
        self.uasm.pop_var(VarName('ret_addr'))
        # If return statement with expression
        if return_stmt.value is not None:
          # Eval return expression
          ret_var_name = self.eval_expr(return_stmt.value)
          if ret_var_name is None:
            raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: Missing value for return expression')
          # Push Retern value
          self.uasm.push_var(ret_var_name)
          # TODO: Add return type check
          # ret_var_type = self.var_table.get_var_type(ret_var_name)
          # if ret_var_type != ...
        # Return
        self.uasm.jump_ret_addr()
      # The compiler skips Import and ImportFrom statements to complete the editor using Python class files.
      # (The compiler does not raise an error when reading Import / ImportFrom statements.)
      elif type(stmt) is ast.Import:
        pass
      elif type(stmt) is ast.ImportFrom:
        pass
      else:
        raise Exception(f'{stmt.lineno}:{stmt.col_offset} {self.print_ast(stmt)}: Unsupported statement.')


  def eval_expr(self, expr: ast.expr) -> Optional[VarName]:
    """
    Eval expression
    """
    # number Expression
    #  | Num(object n) -- a number as a PyObject.
    if type(expr) is ast.Num:
      # FORCE CAST
      num: ast.Num = cast(ast.Num, expr)
      const_var_name = VarName(self.uasm.get_next_id('const'))
      if type(num.n) is int:
        self.var_table.add_var(const_var_name, UdonTypeName('SystemInt32'), f'{num.n}')
      elif type(num.n) is float:
        self.var_table.add_var(const_var_name, UdonTypeName('SystemSingle'), f'{num.n}')
      return const_var_name

    # string Expression
    # | Str(string s) -- need to specify raw, unicode, etc?
    elif type(expr) is ast.Str:
      # FORCE CAST
      _str: ast.Str = cast(ast.Str, expr)
      const_var_name = VarName(self.uasm.get_next_id('const'))
      self.var_table.add_var(const_var_name, UdonTypeName('SystemString'), f'"{_str.s}"')
      return const_var_name

    # Embedded Constant Expression
    # | NameConstant(singleton value)
    elif type(expr) is ast.NameConstant:
      # FORCE CAST
      _const: ast.NameConstant = cast(ast.NameConstant, expr)
      const_var_name = VarName(self.uasm.get_next_id('const'))
      if type(_const.value) is bool and _const.value == True:
        self.var_table.add_var(const_var_name, UdonTypeName('SystemBoolean'), f'null')
        self.uasm.set_bool(const_var_name, True)
      elif type(_const.value) is bool and _const.value == False:
        self.var_table.add_var(const_var_name, UdonTypeName('SystemBoolean'), f'null')
        self.uasm.set_bool(const_var_name, False)
      elif _const.value is None:
        self.var_table.add_var(const_var_name, UdonTypeName('SystemObject'), f'null')
      return const_var_name

    # Variable Expression
    # | Name(identifier id, expr_context ctx)
    elif type(expr) is ast.Name:
      # FORCE CAST
      name: ast.Name = cast(ast.Name, expr)
      return VarName(name.id)

    # Call Expression
    # | Call(expr func, expr* args, keyword* keywords)
    elif type(expr) is ast.Call:
      # FORCE CAST
      _call: ast.Call = cast(ast.Call, expr)
      return self.eval_call(_call)

    # Unary Expression
    #  | UnaryOp(unaryop op, expr operand)
    elif type(expr) is ast.UnaryOp:
      # FORCE CAST
      unary_expr: ast.UnaryOp = cast(ast.UnaryOp, expr)
      operand_var_name = self.eval_expr(unary_expr.operand)
      if operand_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no Unary Expression value.')

      operand_var_type = self.var_table.get_var_type(operand_var_name)
      # -
      if type(unary_expr.op) is ast.USub:
        func_name = 'op_UnaryMinus'
      # not
      if type(unary_expr.op) is ast.Not:
        func_name = 'op_UnaryNegation'
      else:
        raise Exception(f'{unary_expr.lineno}:{unary_expr.col_offset} {self.print_ast(unary_expr)}: Unsupported unary operator.')
      
      ret_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'StaticFunc',
        UdonTypeName(operand_var_type),
        UdonMethodName(func_name), (operand_var_type, ))
      if ret_type_extern_str is not None:
        ret_type, extern_str = ret_type_extern_str
      else:
        raise Exception(f'{unary_expr.lineno}:{unary_expr.col_offset} {self.print_ast(unary_expr)}: {func_name} of {operand_var_type} is undefined.')
      
      unop_result_var_name = VarName(self.uasm.get_next_id('unop'))
      self.var_table.add_var(unop_result_var_name, ret_type, 'null')
      self.uasm.call_extern(extern_str, [operand_var_name, unop_result_var_name])
      return unop_result_var_name

    # Binary Expression
    # | BinOp(expr left, operator op, expr right)
    elif type(expr) is ast.BinOp:
      # FORCE CAST
      bin_expr: ast.BinOp = cast(ast.BinOp, expr)
      binop_left_var_name = self.eval_expr(bin_expr.left)
      binop_right_var_name = self.eval_expr(bin_expr.right)
      if binop_left_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the left side of Binary Expression.')
      if binop_right_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the right side of Binary Expression.')
      left_var_type = self.var_table.get_var_type(binop_left_var_name)
      right_var_type = self.var_table.get_var_type(binop_right_var_name)
      # + 
      if type(bin_expr.op) is ast.Add:
        func_name = 'op_Addition'
      # -
      elif type(bin_expr.op) is ast.Sub:
        func_name = 'op_Subtraction'
      # *
      elif type(bin_expr.op) is ast.Mult:
        func_name = 'op_Multiplication'
      # /
      elif type(bin_expr.op) is ast.Div:
        func_name = 'op_Division'
      else:
        raise Exception(f'{bin_expr.lineno}:{bin_expr.col_offset} {self.print_ast(bin_expr)}: Unsupported binary operator')
      ret_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'StaticFunc',
        UdonTypeName(left_var_type),
        UdonMethodName(func_name), (left_var_type, right_var_type, ))
      if ret_type_extern_str is not None:
        ret_type, extern_str = ret_type_extern_str
      else:
        raise Exception(f'{bin_expr.lineno}:{bin_expr.col_offset} {self.print_ast(expr)}: {func_name} of {left_var_type} and {right_var_type} is undefined.')
      binop_result_var_name = VarName(self.uasm.get_next_id('binop'))
      self.var_table.add_var(binop_result_var_name, ret_type, 'null')
      self.uasm.call_extern(extern_str, [binop_left_var_name, binop_right_var_name, binop_result_var_name])
      return binop_result_var_name

  
    # | Compare(expr left, cmpop* ops, expr* comparators)
    # Limit len(ops) == 1, len(comparators) == 1
    elif type(expr) is ast.Compare:
      # FORCE CAST
      compare: ast.Compare = cast(ast.Compare, expr)
      if not (len(compare.ops) == 1 and len(compare.comparators) == 1):
        raise Exception(f'{compare.lineno}:{compare.col_offset} {self.print_ast(compare)}: Comparison of comparison operators is limited to one by one. (0 <= a <100 cannot be written)')

      compare_result_var_name = VarName(self.uasm.get_next_id('compare'))
      self.var_table.add_var(compare_result_var_name, UdonTypeName('SystemBoolean'), 'null')
      op = compare.ops[0]
      comparator = compare.comparators[0]
      compare_left_var_name = self.eval_expr(compare.left)
      compare_right_var_name = self.eval_expr(comparator)
      if compare_left_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the left side of Compare Expression.')
      if compare_right_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the right side of Compare Expression.')

      left_var_type = self.var_table.get_var_type(compare_left_var_name)
      right_var_type = self.var_table.get_var_type(compare_right_var_name)
      
      # ==
      if type(op) is ast.Eq:
        func_name = 'op_Equality'
      # !=
      elif type(op) is ast.NotEq:
        func_name = 'op_Inequality'
      # <
      elif type(op) is ast.Lt:
        func_name = 'op_LessThan'
      # >
      elif type(op) is ast.Gt:
        func_name = 'op_GreaterThan'
      # <=
      elif type(op) is ast.LtE:
        func_name = 'op_LessThanOrEqual'
      # >=
      elif type(op) is ast.GtE:
        func_name = 'op_GreaterThanOrEqual'
      else:
        raise Exception(f'{compare.lineno}:{compare.col_offset} {self.print_ast(compare)}: Unsupported binary compare operator')
      
      ret_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'StaticFunc',
        UdonTypeName(left_var_type),
        UdonMethodName(func_name), (left_var_type, right_var_type, ))
      if ret_type_extern_str is not None:
        ret_type, extern_str = ret_type_extern_str
      else:
        raise Exception(f'{compare.lineno}:{compare.col_offset} {self.print_ast(expr)}: {func_name} of {left_var_type} and {right_var_type} is undefined.')

      self.uasm.call_extern(extern_str, [compare_left_var_name, compare_right_var_name, compare_result_var_name])
      return compare_result_var_name

    # Logical operator expression
    # BoolOp(boolop op, expr* values)
    # Limited　len(values) == 2
    elif type(expr) is ast.BoolOp:
      # FORCE CAST
      bool_expr: ast.BoolOp = cast(ast.BoolOp, expr)
      if len(bool_expr.values) != 2 :
        raise Exception(f'{bool_expr.lineno}:{bool_expr.col_offset} {self.print_ast(bool_expr)}: Logical operators ("and" and "or") cannot be written consecutively ("A and B and C" must be written as "(A and B) and C").')
      binop_left_var_name = self.eval_expr(bool_expr.values[0])
      binop_right_var_name = self.eval_expr(bool_expr.values[1])
      if binop_left_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the left side of Logical Binary Expression.')
      if binop_right_var_name is None:
        raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: There is no value on the right side of Logical Binary Expression.')
      left_var_type = self.var_table.get_var_type(binop_left_var_name)
      right_var_type = self.var_table.get_var_type(binop_right_var_name)

      # and
      if type(bool_expr.op) is ast.And:
        func_name = 'op_LogicalAnd'
      # or
      elif type(bool_expr.op) is ast.Or:
        func_name = 'op_LogicalOr'
      else:
        raise Exception(f'{bool_expr.lineno}:{bool_expr.col_offset} {self.print_ast(bool_expr)}: Unsupported binary compare operator')
      
      ret_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'StaticFunc',
        UdonTypeName(left_var_type),
        UdonMethodName(func_name), (left_var_type, right_var_type, ))
      if ret_type_extern_str is not None:
        ret_type, extern_str = ret_type_extern_str
      else:
        raise Exception(f'{bool_expr.lineno}:{bool_expr.col_offset} {self.print_ast(expr)}: {func_name} of {left_var_type} and {right_var_type} is undefined.')

      binop_result_var_name = VarName(self.uasm.get_next_id('boolop'))
      self.var_table.add_var(binop_result_var_name, ret_type, 'null')

      self.uasm.call_extern(extern_str, [binop_left_var_name, binop_right_var_name, binop_result_var_name])
      return binop_result_var_name
    else:
      raise Exception(f'{expr.lineno}:{expr.col_offset} {self.print_ast(expr)}: Unsupported expression.')

  # Call Expression
  # | Call(expr func, expr* args, keyword* keywords)
  def eval_call(self, call: ast.Call) -> Optional[VarName]:
    arg_var_names: List[Optional[VarName]] = [self.eval_expr(arg_var_name) for arg_var_name in call.args]
    for i, arg_var_name in enumerate(arg_var_names):
      if arg_var_name is None:
        raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: There is no value on the arg({i}) Expression.')

    # FORCE CAST
    arg_var_types: List[UdonTypeName] = [self.var_table.get_var_type(arg_var_name) for arg_var_name in arg_var_names] # type: ignore

    # AAA.BBBB(arg, ...)
    if type(call.func) is ast.Attribute:
      # FORCE CAST
      return self.eval_call_with_dot(call, arg_var_names, arg_var_types) # type: ignore
    # AAA(arg, ...)
    elif type(call.func) is ast.Name:
      # FORCE CAST
      return self.eval_call_without_dot(call, arg_var_names, arg_var_types) # type: ignore
    else:
      raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: Unsupported binary compare operator.')

  def eval_call_with_dot(self, call: ast.Call, arg_var_names: List[VarName], arg_var_types: List[UdonTypeName]) -> Optional[VarName]:
    func_expr: ast.expr = cast(ast.expr, call.func)
    call_result_var_name = VarName(self.uasm.get_next_id('call'))
    # StaticFunc, Constructor
    # FORCE CAST, NO CHECK
    # BAD CODE
    if type(func_expr.value) is ast.Name and not self.var_table.exist_var(func_expr.value.id):  # type: ignore
      # FORCE CAST, NO CHECK
      module_type: UdonTypeName = UdonTypeName(f'{call.func.value.id}')  # type: ignore
      # FORCE CAST, NO CHECK
      udon_method_name: UdonMethodName = UdonMethodName(f'{call.func.attr}')  # type: ignore
      static_func_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'StaticFunc', module_type,
        udon_method_name, tuple(arg_var_types))
        
      constructor_func_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'Constructor', module_type,
        udon_method_name, tuple(arg_var_types))
      # StaticFunc
      if static_func_type_extern_str is not None:
        ret_type, extern_str = static_func_type_extern_str
        if ret_type != UdonTypeName('None'):
          self.var_table.add_var(call_result_var_name, ret_type, 'null')
          self.uasm.call_extern(extern_str, arg_var_names + [call_result_var_name])
          return call_result_var_name
        else:
          self.uasm.call_extern(extern_str, arg_var_names)
          return None
      # Constructor
      elif constructor_func_type_extern_str is not None:
        ret_type, extern_str = constructor_func_type_extern_str 
        if ret_type != UdonTypeName('None'):
          self.var_table.add_var(call_result_var_name, ret_type, 'null')
          self.uasm.call_extern(extern_str, arg_var_names + [call_result_var_name])
          return call_result_var_name
        else:
          self.uasm.call_extern(extern_str, arg_var_names) 
          return None
      else:
        raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: Udon method {module_type}.{udon_method_name} not found.') 
      
    # InstanceFunc
    # FORCE CAST, NO CHECK
    # BAD CODE
    # elif type(func_expr.value) is ast.expr or (type(func_expr.value) is ast.Name and self.var_table.exist_var(func_expr.value.id)): # type: ignore
    else:
      # FORCE CAST, NO CHECK
      inst_var_name: VarName = self.eval_expr(func_expr.value)  # type: ignore
      inst_var_type: UdonTypeName = self.var_table.get_var_type(inst_var_name)
      # FORCE CAST, NO CHECK
      udon_method_name: UdonMethodName = f'{call.func.attr}' # type: ignore
      instance_func_type_extern_str = self.udon_method_table.get_ret_type_extern_str(
        'InstanceFunc', inst_var_type,
        udon_method_name, tuple(arg_var_types))
      # InstanceFunc
      if instance_func_type_extern_str is not None:
        ret_type, extern_str = instance_func_type_extern_str
        if ret_type != UdonTypeName('None'):
          self.var_table.add_var(call_result_var_name, ret_type, 'null')
          self.uasm.call_extern(extern_str, [inst_var_name] + arg_var_names + [call_result_var_name])
          return call_result_var_name
        else:
          self.uasm.call_extern(extern_str, [inst_var_name] + arg_var_names)
          return None
      else:
        raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: Not Found {inst_var_type}.{udon_method_name}{tuple(arg_var_types)} instance function. ')
    # else:
    #   raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: Unsupported function format.')
    return call_result_var_name

  def eval_call_without_dot(self, call: ast.Call, arg_var_names: List[VarName], arg_var_types: List[UdonTypeName]) -> Optional[VarName]:
    # FORCE CAST, NO CHECK
    org_func: FuncName = f'{call.func.id}'  # type: ignore
    # Embedded functions
    if org_func == 'instantiate':
      if len(arg_var_names) != 1:
        raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: instantiate must have exactly one argument.')
      arg_var_name: VarName = arg_var_names[0]
      instantiate_var_name = VarName(self.uasm.get_next_id('instantiate'))
      self.var_table.add_var(
        instantiate_var_name, UdonTypeName('UnityEngineGameObject'), 'null')
      self.uasm.call_extern(
        ExternStr('VRCInstantiate.__Instantiate__UnityEngineGameObject__UnityEngineGameObject'),
        [arg_var_name, instantiate_var_name])
      return instantiate_var_name
    # Force Cast
    elif org_func in udon_types:
      cast_type = UdonTypeName(org_func)
      cast_var_name = VarName(self.uasm.get_next_id('cast'))
      if len(arg_var_names) != 1:
        raise Exception(f'{call.lineno}:{call.col_offset} {self.print_ast(call)}: A cast argument must be exactly one.')
      arg_var_name = arg_var_names[0]
      self.var_table.add_var(cast_var_name, cast_type, 'null')
      self.uasm.assign(cast_var_name, arg_var_name)
      return cast_var_name
    
    # Call defined fuction
    else:
      return self.uasm.call_def_func(org_func, arg_var_names)

if __name__ == '__main__':
  arg_parser = argparse.ArgumentParser(description='UdonPie language Udon Assembly compiler', add_help=True)
  arg_parser.add_argument('input', help='input UdonPie source code path (ex: .\example.py)')
  arg_parser.add_argument('output', help='output Udon Assembly code path (ex: .\example.uasm)')
  args = arg_parser.parse_args()

  try:
    f = open(args.input, encoding="utf-8")
    pycode = f.read()
    f.close()
    comp = UdonCompiler(pycode)
    asm = comp.make_uasm_code()
    f = open(args.output, 'w')
    f.write(asm)
    f.close()
  except Exception as ex:
    print(ex)

