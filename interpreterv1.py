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
        self.classes[name] = Recipe(name, body, super().get_input,
                                    super().output, super().error,
                                    self.trace_output)


class Recipe:
    """
    Class definition
    """
    def __init__(self, name: SWLN, body: list, get_input: InputFun,
                 output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output
        self.fields: dict[SWLN, Ingredient] = {}
        self.methods: dict[SWLN, Instruction] = {}

        for definition in body:
            match definition:
                case [InterpreterBase.FIELD_DEF, name, value] \
                        if isSWLN(name) and isSWLN(value):
                    self.add_field(name, value)
                case [InterpreterBase.METHOD_DEF, name, list(params),
                      statement] if isSWLN(name) and all(map(isSWLN, params)):
                    self.add_method(name, params, statement)
                case _:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Not a field or method: {definition}")

    def __copy__(self):
        tea = Recipe(self.name, [], self.get_input, self.output, self.error,
                     self.trace_output)
        for name, leaf in self.fields.items():
            tea.add_field(name, leaf.value)
        for steep in self.methods.values():
            tea.add_method(steep.name, steep.formals, steep.statement)
        return tea

    def __str__(self) -> str:
        return f'<class {self.name}>'

    def add_field(self, name: SWLN, value: BrewinTypes):
        if name in self.fields:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate fields in {self.name}: {name}",
                       name.line_num)
        try:
            self.fields[name] = Ingredient(value, self.error, self.trace_output)
        except ValueError:
            self.error(ErrorType.SYNTAX_ERROR, f"Not a valid value: {value}",
                       value.line_num)

    def add_method(self, name: SWLN, params: list[SWLN], statement):
        if name in self.methods:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate methods in {self.name}: {name}",
                       name.line_num)
        self.methods[name] = Instruction(name, params, statement, self,
                                         self.fields, self.get_input,
                                         self.output, self.error,
                                         self.trace_output)


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


class Instruction:
    """
    Method definition
    """
    def __init__(self, name: SWLN, params: list[SWLN], statement: list,
                 me: Recipe, scope: dict[SWLN, Ingredient], get_input: InputFun,
                 output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.formals = params
        self.statement = statement
        self.me = me
        self.scope = scope
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output

    def call(self, *args: list[Ingredient],
             classes: dict[SWLN]) -> None | Ingredient:
        """
        Throws ValueError on wrong number of arguments
        """
        parameters = {formal: actual for formal, actual
                      in zip(self.formals, args, strict=True)}

        is_return, beans = evaluate_statement(self.statement, self.me, classes,
                                              parameters, self.scope,
                                              self.get_input, self.output,
                                              self.error, self.trace_output)
        if is_return:
            return beans
        else:
            return None


def evaluate_expression(expression, me: Recipe, classes: dict[SWLN, Recipe],
                        parameters: dict[SWLN, Ingredient],
                        scope: dict[SWLN, Ingredient],
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
            return parameters[variable]
        case variable if isSWLN(variable) and variable in scope:
            return scope[variable]
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
                    blend = bool(grounds is cream)
                case '!=' if ((grounds is None or isinstance(grounds, Recipe))
                              and (cream is None or isinstance(cream, Recipe))):
                    blend = bool(grounds is not cream)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {binary_operator} is compatible with "
                        f"expression types: {type(grounds)}, {type(cream)}",
                        binary_operator.line_num)
            if trace_output:
                debug(f"{type(blend)=}")
            return Ingredient(blend, error, trace_output)
        case [sub_expression]:
            return evaluate_expression(sub_expression, me, classes, parameters,
                                       scope, error, trace_output)
        case _:
            error(ErrorType.SYNTAX_ERROR,
                  f"Not a valid expression: {expression}")


def evaluate_statement(statement, me: Recipe, classes: dict[SWLN, Recipe],
                       parameters: dict[SWLN, Ingredient],
                       scope: dict[SWLN, Ingredient], get_input: InputFun,
                       output: OutputFun, error: ErrorFun, trace_output: bool) \
                        -> Tuple[bool, None | Ingredient]:
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
        case [InterpreterBase.BEGIN_DEF, sub_statement1, *sub_statements]:
            latest_order = evaluate_statement(sub_statement1, me, classes,
                                              parameters, scope, get_input,
                                              output, error, trace_output)
            if latest_order[0]:
                return latest_order
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
                parameters[variable] = Ingredient(int(get_input()), error,
                                                  trace_output)
            elif variable in scope:
                scope[variable] = Ingredient(int(get_input()), error,
                                             trace_output)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.INPUT_STRING_DEF, variable] if isSWLN(variable):
            if variable in parameters:
                parameters[variable] = Ingredient(str(get_input()), error,
                                                  trace_output)
            elif variable in scope:
                scope[variable] = Ingredient(str(get_input()), error,
                                             trace_output)
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
                scope[variable] = evaluate_expression(expression, me, classes,
                                                      parameters, scope, error,
                                                      trace_output)
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
        case [sub_statement]:
            return evaluate_statement(sub_statement)
        case _:
            error(ErrorType.SYNTAX_ERROR, f"Not a valid statement: {statement}")
    return False, None


Interpreter = Barista


def main():
    interpreter = Interpreter(trace_output=True)
    script = '''
            (class person
                (field name "")
                (field age 0)
                (method init (n a)
                    (begin
                    (set name n)
                    (set age a)
                    )
                )
                (method talk (to_whom)
                    (print name " says hello to " to_whom)
                )
            )

            (class main
                (field p null)
                (method tell_joke (to_whom)
                    (print "Hey " to_whom ", knock knock!")
                )
                (method main ()
                    (begin
                        (call me tell_joke "Matt") # call tell_joke in current object
                        (set p (new person))  # allocate a new person obj, point p at it
                        (call p init "Siddarth" 25) # call init in object pointed to by p
                        (call p talk "Paul")       # call talk in object pointed to by p
                    )
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
