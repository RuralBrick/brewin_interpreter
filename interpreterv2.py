"""
Reference:

Barista - Interpreter;

Recipe - class definition;
cuppa - object;
tea - new object/copy of class definition;
cup_of_the_day - main object;

Instruction - method;
brew - object's method;
steep - copy of method;
recommended_brew - main object's method;
service - result of a method call;
order - result of a statement;

Tin - variable;
bag - copy of variable;

Ingredient - boxed value;
beans - instantiated Ingredient;
grounds - value;
cream - secondary value;
leaf - copy of field value;
roast - value after unary operation;
blend - value after binary operation;

bear - Brewin error;
rare - RuntimeError;
"""

from typing import Callable, Union, Tuple
import copy
import sys
import pprint

from intbase import InterpreterBase, ErrorType
from bparser import BParser, StringWithLineNumber as SWLN


InputFun = Callable[[], str]
OutputFun = Callable[[str], None]
ErrorFun = Callable[[ErrorType, str, int], None]
BrewinTypes = Union[SWLN, int, str, bool, 'Recipe', None]
isSWLN = lambda token: isinstance(token, SWLN)
isVarType = (lambda token, me, classes:
             token in {InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF,
                       InterpreterBase.BOOL_DEF, me.name}.union(classes))
isMethodType = (lambda token, me, classes:
                token in {InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF,
                          InterpreterBase.BOOL_DEF, InterpreterBase.VOID_DEF,
                          me.name}.union(classes))
debug = lambda *values: print(*values, file=sys.stderr, flush=True)


class Barista(InterpreterBase):
    """
    Interpreter
    """
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def run(self, program: list[str]):
        well_formed, tokens = BParser.parse(program)

        if not well_formed:
            super().error(ErrorType.SYNTAX_ERROR, tokens)

        if self.trace_output:
            debug("Line numbers:")
            pprint.pprint(tokens, stream=sys.stderr)
            debug()

        self.init()

        for class_def in tokens:
            match class_def:
                case [InterpreterBase.CLASS_DEF, name,
                      InterpreterBase.INHERITS_DEF, parent_name,
                      *body] if isSWLN(name) and isSWLN(parent_name):
                    # TODO use parent_name
                    self.add_class(name, body)
                case [InterpreterBase.CLASS_DEF, name, *body] if isSWLN(name):
                    self.add_class(name, body)
                case _:
                    super().error(ErrorType.SYNTAX_ERROR,
                                  f"Not a class: {class_def}")

        if self.trace_output:
            debug("Parsed classes:")
            for recipe in self.classes.values():
                debug(f"  class {recipe.name}")
                debug("  fields:")
                for name, ingredient in recipe.fields.items():
                    debug(f"    {name}={ingredient.value}")
                debug("  methods:")
                for instruction in recipe.methods.values():
                    debug(f"    {instruction.name}({instruction.formals})=")
                    debug(f"{pprint.pformat(instruction.statement)}")
            debug("\nStarting execution...")

        try:
            cup_of_the_day = copy.copy(
                self.classes[InterpreterBase.MAIN_CLASS_DEF]
            )
        except KeyError:
            super().error(ErrorType.SYNTAX_ERROR, "Main class not found")

        try:
            recommended_brew = cup_of_the_day.methods[
                InterpreterBase.MAIN_FUNC_DEF
            ]
        except KeyError:
            super().error(ErrorType.SYNTAX_ERROR, "Main method not found")

        try:
            recommended_brew.call(classes=self.classes)
        except ValueError:
            super().error(ErrorType.SYNTAX_ERROR,
                          "Main method cannot accept arguments")

    def init(self):
        self.classes: dict[SWLN, Recipe] = {}

    def add_class(self, name: SWLN, body: list):
        if name in self.classes:
            super().error(ErrorType.TYPE_ERROR, f"Duplicate classes: {name}",
                          name.line_num)
        self.classes[name] = Recipe(name, body, self.classes, super().get_input,
                                    super().output, super().error,
                                    self.trace_output)


class Recipe:
    """
    Class definition
    """
    def __init__(self, name: SWLN, body: list, classes: dict[SWLN, 'Recipe'],
                 get_input: InputFun, output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.parent: Recipe = None # TODO
        self.classes = classes
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output
        self.fields: dict[SWLN, Tin] = {}
        self.methods: dict[SWLN, Instruction] = {}

        for definition in body:
            match definition:
                case [InterpreterBase.FIELD_DEF, btype, name, value] \
                        if isSWLN(btype) and isSWLN(name) and isSWLN(value):
                    self.add_field(name, btype, value)
                case [InterpreterBase.METHOD_DEF, InterpreterBase.INT_DEF
                      |InterpreterBase.STRING_DEF|InterpreterBase.BOOL_DEF
                      |InterpreterBase.VOID_DEF, name, params, statement] \
                        if isSWLN(name):
                    # TODO: Add type
                    self.add_method(name, params, statement)
                case [InterpreterBase.METHOD_DEF, class_name, name, params,
                      statement] if isSWLN(class_name) and isSWLN(name):
                    # TODO: Add type
                    # TODO: Check if class exists
                    self.add_method(name, params, statement)
                case _:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Not a field or method: {definition}")

    def __copy__(self):
        tea = Recipe(self.name, [], self.classes, self.get_input, self.output,
                     self.error, self.trace_output)
        for name, bag in self.fields.items():
            tea.add_field(name, bag.btype, bag.value.value)
        for steep in self.methods.values():
            tea.add_method(steep.name, steep.formals, steep.statement)
        return tea

    def __str__(self) -> str:
        return f'<class {self.name}>'

    def add_field(self, name: SWLN, btype: SWLN, value: BrewinTypes):
        if name in self.fields:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate fields in {self.name}: {name}",
                       name.line_num)
        try:
            beans = Ingredient(value, self.error, self.trace_output)
            self.fields[name] = Tin(name, btype, beans, self, self.classes,
                                    self.error)
        except ValueError:
            self.error(ErrorType.SYNTAX_ERROR, f"Not a valid value: {value}",
                       value.line_num)

    def add_method(self, name: SWLN, params, statement):
        if name in self.methods:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate methods in {self.name}: {name}",
                       name.line_num)
        self.methods[name] = Instruction(name, params, statement, self,
                                         self.classes, self.fields,
                                         self.get_input, self.output,
                                         self.error, self.trace_output)

    def is_instance(self, class_name: SWLN) -> bool:
        return self.name == class_name or (self.parent and
                                           self.parent.is_instance(class_name))


class Ingredient:
    """
    Field definition
    """
    def __init__(self, value: BrewinTypes, error: ErrorFun,
                 trace_output: bool) -> None:
        """
        Throws ValueError on invalid value
        """
        self.error = error
        self.trace_output = trace_output

        match value:
            case grounds if not isSWLN(grounds):
                if self.trace_output:
                    debug(f"Raw value to Ingredient: {grounds}:{type(grounds)}")
                self.value = value
            case InterpreterBase.NULL_DEF:
                self.value = None
            case InterpreterBase.TRUE_DEF:
                self.value = True
            case InterpreterBase.FALSE_DEF:
                self.value = False
            case str_or_int:
                try:
                    if str_or_int[0] == '"' and str_or_int[-1] == '"':
                        self.value = str_or_int[1:-1]
                    else:
                        self.value = int(str_or_int)
                except IndexError:
                    self.error(ErrorType.SYNTAX_ERROR, "Blank value, somehow",
                               value.line_num)

    def __str__(self) -> str:
        match self.value:
            case True:
                return InterpreterBase.TRUE_DEF
            case False:
                return InterpreterBase.FALSE_DEF
            case None:
                return InterpreterBase.NULL_DEF
        return str(self.value)


class Tin:
    """
    Variable definition
    """
    def __init__(self, name: SWLN, btype: SWLN, boxed_value: Ingredient,
                 me: Recipe, classes: dict[SWLN, Recipe], error: ErrorFun) \
                    -> None:
        self.name = name
        self.error = error

        if isVarType(btype, me, classes):
            self.btype = btype
        else:
            self.error(ErrorType.TYPE_ERROR, f"Class {btype} not defined above",
                       btype.line_num)

        try:
            self.set_value(boxed_value)
        except TypeError as e:
            self.error(ErrorType.TYPE_ERROR, str(e), self.name.line_num)

    def set_value(self, boxed_value: Ingredient):
        """
        Throws TypeError on incompatible type
        """
        grounds = boxed_value.value
        match self.btype:
            case InterpreterBase.INT_DEF:
                if type(grounds) == int:
                    self.value = boxed_value
                    return
            case InterpreterBase.STRING_DEF:
                if type(grounds) == str:
                    self.value = boxed_value
                    return
            case InterpreterBase.BOOL_DEF:
                if type(grounds) == bool:
                    self.value = boxed_value
                    return
            case class_name:
                if grounds is None:
                    self.value = boxed_value
                    return
                if grounds.is_instance(class_name):
                    self.value = boxed_value
                    return
                raise TypeError(f"Class {grounds.name} not derived from "
                                f"{class_name}")
        match type(grounds):
            case int():
                raise TypeError(f"Cannot assign value of type"
                                f"{InterpreterBase.INT_DEF} to variable of "
                                f"type {self.btype}")
            case str():
                raise TypeError(f"Cannot assign value of type"
                                f"{InterpreterBase.STRING_DEF} to variable of "
                                f"type {self.btype}")
            case bool():
                raise TypeError(f"Cannot assign value of type "
                                f"{InterpreterBase.BOOL_DEF} to variable of "
                                f"type {self.btype}")
            case _:
                raise TypeError(f"Cannot assign object to variable of type "
                                f"{self.btype}")


class Instruction:
    """
    Method definition
    """
    def __init__(self, name: SWLN, params, statement, me: Recipe,
                 classes: dict[SWLN, Recipe], scope: dict[SWLN, Tin],
                 get_input: InputFun, output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.statement = statement
        self.me = me
        self.classes = classes
        self.scope = scope
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output
        self.formals: dict[SWLN, SWLN] = {}

        for param in params:
            match param:
                case formal if isSWLN(formal):
                    self.formals[formal] = params[formal]
                case [btype, formal] if isSWLN(btype) and isSWLN(formal):
                    self.add_parameter(formal, btype)
                case _:
                    error(ErrorType.SYNTAX_ERROR,
                          f"Malformed parameter: {param}", name.line_num)

    def call(self, *args: Ingredient,
             classes: dict[SWLN, Recipe]) -> Ingredient | None:
        """
        Throws ValueError on wrong number of arguments
        """
        parameters = {formal: Tin(formal, btype, actual, self.me, self.classes,
                                  self.error)
                      for (formal, btype), actual
                      in zip(self.formals.items(), args, strict=True)}

        is_return, beans = evaluate_statement(self.statement, self.me, classes,
                                              parameters, self.scope,
                                              self.get_input, self.output,
                                              self.error, self.trace_output)
        if is_return:
            return beans
        else:
            return None

    def add_parameter(self, name: SWLN, btype: SWLN):
        if name in self.formals:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate parameters in {self.name}: name",
                       name.line_num)
        if not isVarType(btype, self.me, self.classes):
            self.error(ErrorType.TYPE_ERROR, f"Class {btype} not defined above",
                       btype.line_num)
        self.formals[name] = btype


def evaluate_expression(expression, me: Recipe, classes: dict[SWLN, Recipe],
                        parameters: dict[SWLN, Tin], scope: dict[SWLN, Tin],
                        error: ErrorFun, trace_output: bool) -> Ingredient:
    """
    Guaranteed to return a boxed value (or throw a Brewin error if unable to)
    """
    if trace_output:
        if type(expression) == list:
            try:
                debug(f"line {expression[0].line_num}: Expression starts with "
                    f"{expression[0]}")
            except IndexError:
                debug("Empty expression")
            except AttributeError:
                debug(f"no line_num: Expression starts with {expression[0]}")
        else:
            try:
                debug(f"line {expression.line_num}: Expression is {expression}")
            except AttributeError:
                debug(f"no line_num: Expression is {expression}")
    match expression:
        case InterpreterBase.ME_DEF:
            return Ingredient(me, error, trace_output)
        case variable if isSWLN(variable) and variable in parameters:
            return parameters[variable].value
        case variable if isSWLN(variable) and variable in scope:
            return scope[variable].value
        case const if isSWLN(const):
            try:
                return Ingredient(const, error, trace_output)
            except ValueError:
                error(ErrorType.NAME_ERROR, f"Variable not found: {const}",
                      const.line_num)
        case [InterpreterBase.CALL_DEF, obj_expression, method, *arguments] \
                if isSWLN(method):
            cuppa = evaluate_expression(obj_expression, me, classes, parameters,
                                        scope, error, trace_output).value
            if cuppa is None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr", expression[0].line_num)
            try:
                brew = cuppa.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Object does not have method: {method}", method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR,
                      f"Method being called on non-object",
                      expression[0].line_num)
            try:
                service = brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                          scope, error, trace_output)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {method}",
                      expression[0].line_num)
            if service is None:
                error(ErrorType.TYPE_ERROR,
                      f"Method did not return a value: {method}",
                      expression[0].line_num)
            else:
                return service
        case [InterpreterBase.NEW_DEF, name] if isSWLN(name):
            try:
                cuppa = classes[name]
            except KeyError:
                error(ErrorType.TYPE_ERROR, f"Could not find class: {name}",
                      expression[0].line_num)
            return Ingredient(copy.copy(cuppa), error, trace_output)
        case [unary_operator, sub_expression] if isSWLN(unary_operator):
            grounds = evaluate_expression(sub_expression, me, classes,
                                          parameters, scope, error,
                                          trace_output).value
            if trace_output:
                debug(f"{unary_operator=} with {grounds=}:{type(grounds)}")
            match unary_operator:
                case '!' if type(grounds) == bool:
                    roast = bool(not grounds)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {unary_operator} is compatible with "
                        f"expression type: {type(grounds)}",
                        unary_operator.line_num)
            if trace_output:
                debug(f"{type(roast)=}")
            return Ingredient(roast, error, trace_output)
        case [binary_operator, left_expression, right_expression]:
            grounds = evaluate_expression(left_expression, me, classes,
                                          parameters, scope, error,
                                          trace_output).value
            cream = evaluate_expression(right_expression, me, classes,
                                        parameters, scope, error,
                                        trace_output).value
            if trace_output:
                debug(f"{binary_operator=} with {grounds=}:{type(grounds)} and "
                      f"{cream=}:{type(cream)}")
            match binary_operator:
                # NOTE: `eval` only used after operator becomes known to prevent
                #       arbitrary code execution
                case '+'|'-'|'*'|'/'|'%' if type(grounds) == type(cream) == int:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = int(operator(grounds, cream))
                case '<'|'>'|'<='|'>='|'!='|'==' \
                        if type(grounds) == type(cream) == int:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '+' if type(grounds) == type(cream) == str:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = str(operator(grounds, cream))
                case '=='|'!='|'<'|'>'|'<='|'>=' \
                        if type(grounds) == type(cream) == str:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '!='|'==' if type(grounds) == type(cream) == bool:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '&' if type(grounds) == type(cream) == bool:
                    blend = bool(grounds and cream)
                case '|' if type(grounds) == type(cream) == bool:
                    blend = bool(grounds or cream)
                case '==' if ((grounds is None or isinstance(grounds, Recipe))
                              and (cream is None or isinstance(cream, Recipe))):
                    # TODO: Check inheritance
                    blend = bool(grounds is cream)
                case '!=' if ((grounds is None or isinstance(grounds, Recipe))
                              and (cream is None or isinstance(cream, Recipe))):
                    # TODO: Check inheritance
                    blend = bool(grounds is not cream)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {binary_operator} is compatible with "
                        f"expression types: {type(grounds)}, {type(cream)}",
                        binary_operator.line_num)
            if trace_output:
                debug(f"{type(blend)=}")
            return Ingredient(blend, error, trace_output)
        case _:
            error(ErrorType.SYNTAX_ERROR,
                  f"Not a valid expression: {expression}")


def evaluate_statement(statement, me: Recipe, classes: dict[SWLN, Recipe],
                       parameters: dict[SWLN, Tin], scope: dict[SWLN, Tin],
                       get_input: InputFun, output: OutputFun, error: ErrorFun,
                       trace_output: bool) -> Tuple[bool, None | Ingredient]:
    """
    Returns a tuple of the form (<if the method is returning>, <the boxed value
    of the return, if there is one>)
    """
    if trace_output:
        try:
            debug(f"line {statement[0].line_num}: Running {statement[0]}")
        except IndexError:
            debug("Empty statement")
        except AttributeError:
            debug(f"no line_num: Running {statement[0]}")
    match statement:
        case [InterpreterBase.BEGIN_DEF, *sub_statements] if sub_statements:
            for sub_statement in sub_statements:
                latest_order = evaluate_statement(sub_statement, me, classes,
                                                  parameters, scope, get_input,
                                                  output, error, trace_output)
                if latest_order[0]:
                    return latest_order
        case [InterpreterBase.CALL_DEF, expression, method, *arguments] \
                if isSWLN(method):
            cuppa = evaluate_expression(expression, me, classes, parameters,
                                        scope, error, trace_output).value
            if cuppa is None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr", statement[0].line_num)
            try:
                brew = cuppa.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Object does not have method: {method}", method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR,
                      f"Method being called on non-object",
                      statement[0].line_num)
            try:
                brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                          scope, error, trace_output)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {method}",
                      statement[0].line_num)
        case [InterpreterBase.IF_DEF, expression, true_statement]:
            condition = evaluate_expression(expression, me, classes, parameters,
                                            scope, error, trace_output).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                order = evaluate_statement(true_statement, me, classes,
                                           parameters, scope, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
        case [InterpreterBase.IF_DEF, expression, true_statement,
              false_statement]:
            condition = evaluate_expression(expression, me, classes, parameters,
                                            scope, error, trace_output).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                order = evaluate_statement(true_statement, me, classes,
                                           parameters, scope, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
            else:
                order = evaluate_statement(false_statement, me, classes,
                                           parameters, scope, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
        case [InterpreterBase.INPUT_INT_DEF, variable] if isSWLN(variable):
            if variable in parameters:
                try:
                    beans = Ingredient(int(get_input()), error, trace_output)
                except ValueError:
                    error(ErrorType.TYPE_ERROR,
                          "Could not convert input to integer",
                          statement[0].line_num)
                except TypeError:
                    error(ErrorType.TYPE_ERROR, "Expected input but got none",
                          statement[0].line_num)
                try:
                    parameters[variable].set_value(beans)
                except TypeError as e:
                    error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
            elif variable in scope:
                try:
                    beans = Ingredient(int(get_input()), error, trace_output)
                except ValueError:
                    error(ErrorType.TYPE_ERROR,
                          "Could not convert input to integer",
                          statement[0].line_num)
                except TypeError:
                    error(ErrorType.TYPE_ERROR, "Expected input but got none",
                          statement[0].line_num)
                try:
                    scope[variable].set_value(beans)
                except TypeError as e:
                    error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.INPUT_STRING_DEF, variable] if isSWLN(variable):
            if variable in parameters:
                beans = Ingredient(str(get_input()), error, trace_output)
                try:
                    parameters[variable].set_value(beans)
                except TypeError as e:
                    error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
            elif variable in scope:
                beans = Ingredient(str(get_input()), error, trace_output)
                try:
                    scope[variable].set_value(beans)
                except TypeError as e:
                    error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.PRINT_DEF, *arguments]:
            if trace_output:
                debug(output)
            output(
                ''.join(
                    str(
                        evaluate_expression(argument, me, classes, parameters,
                                            scope, error, trace_output)
                    )
                    for argument in arguments
                )
            )
        case [InterpreterBase.RETURN_DEF]:
            return True, None
        case [InterpreterBase.RETURN_DEF, expression]:
            return True, evaluate_expression(expression, me, classes,
                                             parameters, scope, error,
                                             trace_output)
        case [InterpreterBase.SET_DEF, variable, expression] \
                if isSWLN(variable):
            if variable in parameters:
                parameters[variable] = evaluate_expression(expression, me,
                                                           classes, parameters,
                                                           scope, error,
                                                           trace_output)
            elif variable in scope:
                beans = evaluate_expression(expression, me, classes, parameters,
                                            scope, error, trace_output)
                try:
                    scope[variable].set_value(beans)
                except TypeError as e:
                    error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.WHILE_DEF, expression, statement_to_run]:
            while True:
                condition = evaluate_expression(expression, me, classes,
                                                parameters, scope, error,
                                                trace_output).value
                if type(condition) != bool:
                    error(ErrorType.TYPE_ERROR,
                          "Condition did not evaluate to boolean",
                          statement[0].line_num)
                if not condition:
                    break
                latest_order = evaluate_statement(statement_to_run, me, classes,
                                                  parameters, scope, get_input,
                                                  output, error, trace_output)
                if latest_order[0]:
                    return latest_order
        case [InterpreterBase.LET_DEF, var_defs, *sub_statements] \
                if sub_statements:
            for var_def in var_defs:
                match var_def:
                    case [InterpreterBase.INT_DEF|InterpreterBase.STRING_DEF
                          |InterpreterBase.BOOL_DEF, name, value] \
                            if isSWLN(name) and isSWLN(value):
                        pass # TODO
                    case [class_name, name, value] if isSWLN(class_name) \
                                                      and isSWLN(name) \
                                                      and isSWLN(value):
                        pass # TODO
                    case _:
                        error(ErrorType.SYNTAX_ERROR,
                              f"Malformed local variable: {var_def}",
                              statement[0].line_num)
            # TODO: Finish
        case _:
            error(ErrorType.SYNTAX_ERROR, f"Not a valid statement: {statement}")
    return False, None


Interpreter = Barista


def main():
    interpreter = Interpreter(trace_output=True)
    script = '''
(class main
(method void foo ((int param1) (string param2))
  (set param1 param2)
)

  (method void main ()
    (call me foo 17 "kevin")
  )
)
    '''
    try:
        interpreter.run(script.splitlines())
        print(interpreter.get_output())
    except RuntimeError as rare:
        print(rare)
        print(interpreter.get_error_type_and_line())


if __name__ == '__main__':
    main()
