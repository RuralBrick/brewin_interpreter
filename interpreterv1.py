from typing import Callable
import copy

from intbase import InterpreterBase, ErrorType
from bparser import BParser, StringWithLineNumber as SWLN


InputFun = Callable[[], str]
OutputFun = Callable[[str], None]
ErrorFun = Callable[[ErrorType, str, int], None]
isSWLN = lambda token: isinstance(token, SWLN)


class Barista(InterpreterBase):
    """
    Interpreter
    """
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.get_input = super().get_input
        self.output = super().output
        self.error = super().error

    def init(self):
        self.classes: dict[SWLN, Recipe] = {}

    def add_class(self, name: SWLN, body: list):
        if name in self.classes:
            self.error(ErrorType.NAME_ERROR, f"Duplicate classes: {name}")
        self.classes[name] = Recipe(name, body, self.get_input, self.output,
                                    self.error)

    def run(self, program: list[str]):
        well_formed, tokens = BParser.parse(program)

        if not well_formed:
            self.error(ErrorType.SYNTAX_ERROR, tokens)

        self.init()

        for class_def in tokens:
            match class_def:
                case [InterpreterBase.CLASS_DEF, name, *body] if isSWLN(name):
                    self.add_class(name, body)
                case _:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Not a class: {class_def}")

        try:
            cup_of_the_day = self.classes[InterpreterBase.MAIN_CLASS_DEF]
        except KeyError:
            self.error(ErrorType.SYNTAX_ERROR, "Main class not found")

        try:
            recommended_brew = cup_of_the_day.methods[
                InterpreterBase.MAIN_FUNC_DEF
            ]
        except KeyError:
            self.error(ErrorType.SYNTAX_ERROR, "Main method not found")

        try:
            recommended_brew.call(classes=self.classes)
        except ValueError:
            self.error(ErrorType.SYNTAX_ERROR,
                       "Main method cannot accept arguments")


Interpreter = Barista


class Recipe:
    """
    Class definition
    """
    def __init__(self, name: SWLN, body: list, get_input: InputFun,
                 output: OutputFun, error: ErrorFun) -> None:
        self.name = name
        self.get_input = get_input
        self.output = output
        self.error = error
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

    def add_field(self, name: SWLN, value: SWLN):
        if name in self.fields:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate fields in {self.name}: {name}",
                       name.line_num)
        self.fields[name] = Ingredient(value, self.error)

    def add_method(self, name: SWLN, params: list[SWLN], statement):
        if name in self.methods:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate methods in {self.name}: {name}",
                       name.line_num)
        self.methods[name] = Instruction(name, params, statement, self,
                                         self.fields, self.get_input,
                                         self.output, self.error)


class Ingredient:
    """
    Field definition
    """
    def __init__(self, value: SWLN | int | str | bool | Recipe | None,
                 error: ErrorFun) -> None:
        self.error = error

        match value:
            case value if not isSWLN(value):
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
                except ValueError:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Invalid value: {value}", value.line_num)

    def __repr__(self) -> str:
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
                 output: OutputFun, error: ErrorFun) -> None:
        self.name = name
        self.formals = params
        self.statement = statement
        self.me = me
        self.scope = scope
        self.get_input = get_input
        self.output = output
        self.error = error

    def __repr__(self) -> str:
        return f'{self.name}({self.formals}) = {str(self.statement):.32}...'

    def call(self, *args: list[Ingredient],
             classes: dict[SWLN]) -> None | Ingredient:
        """
        Throws ValueError on wrong number of arguments
        """
        parameters = {formal: actual for formal, actual
                      in zip(self.formals, args, strict=True)}

        return evaluate_statement(self.statement, self.me, classes, parameters,
                                  self.scope, self.get_input, self.output,
                                  self.error)


def evaluate_expression(expression, me: Recipe, classes: dict[SWLN, Recipe],
                        parameters: dict[SWLN, Ingredient],
                        scope: dict[SWLN, Ingredient],
                        error: ErrorFun) -> Ingredient:
    match expression:
        case variable if isSWLN(variable) and variable in parameters:
            return parameters[variable]
        case variable if isSWLN(variable) and variable in scope:
            return scope[variable]
        case const if isSWLN(const):
            return Ingredient(const, error)
        case [InterpreterBase.CALL_DEF, InterpreterBase.ME_DEF, method,
              *arguments] if isSWLN(method):
            try:
                signature_brew = me.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Could not find method: {InterpreterBase.ME_DEF}."
                      f"{method}",
                      method.line_num)
            try:
                result = signature_brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                         scope, error)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {obj}."
                      f"{method}",
                      expression[0].line_num)
            if result == None:
                error(ErrorType.TYPE_ERROR,
                      f"Statement did not return a value: "
                      f"{InterpreterBase.ME_DEF}.{method}",
                      expression[0].line_num)
            else:
                return result
        case [InterpreterBase.CALL_DEF, obj, method, *arguments] \
                if isSWLN(obj) and isSWLN(method):
            try:
                cuppa = scope[obj].value
            except KeyError:
                error(ErrorType.NAME_ERROR, f"Could not find object: {obj}",
                      obj.line_num)
            if cuppa == None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr: {obj}",
                      obj.line_num)
            try:
                brew = cuppa.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Could not find method: {obj}.{method}",
                      method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR, f"Not an object: {obj}",
                      obj.line_num)
            try:
                result = brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                         scope, error)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {obj}."
                      f"{method}",
                      expression[0].line_num)
            if result == None:
                error(ErrorType.TYPE_ERROR,
                      f"Statement did not return a value: {obj}.{method}",
                      expression[0].line_num)
            else:
                return result
        case [InterpreterBase.NEW_DEF, name] if isSWLN(name):
            try:
                cuppa = classes[name]
            except KeyError:
                error(ErrorType.TYPE_ERROR, f"Could not find class: {name}",
                      expression[0].line_num)
            return Ingredient(copy.deepcopy(cuppa), error)
        case [unary_operator, expression] if isSWLN(unary_operator):
            beans = evaluate_expression(expression, me, classes, parameters,
                                        scope, error).value
            match unary_operator:
                case '!' if type(beans) == bool:
                    roast = not beans
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {unary_operator} is compatible with "
                        f"expression type: {type(beans)}",
                        unary_operator.line_num)
            return Ingredient(roast, error)
        case [binary_operator, left_expression, right_expression]:
            beans = evaluate_expression(left_expression, me, classes,
                                        parameters, scope, error).value
            cream = evaluate_expression(right_expression, me, classes,
                                        parameters, scope, error).value
            match binary_operator:
                # NOTE: `eval` only used after operator becomes known to prevent
                #       arbitrary code execution
                case '+'|'-'|'*'|'/'|'%'|'<'|'>'|'<='|'>='|'!='|'==' \
                        if type(beans) == type(cream) == int:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = operator(beans, cream)
                case '+'|'=='|'!='|'<'|'>'|'<='|'>=' \
                        if type(beans) == type(cream) == str:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = operator(beans, cream)
                case '!='|'=='|'&'|'|' if type(beans) == type(cream) == bool:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = operator(beans, cream)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {binary_operator} is compatible with "
                        f"expression types: {type(beans)}, {type(cream)}",
                        binary_operator.line_num)
            return Ingredient(blend, error)
        case _:
            error(ErrorType.SYNTAX_ERROR,
                  f"Not a valid expression: {expression}")


def evaluate_statement(statement, me: Recipe, classes: dict[SWLN, Recipe],
                       parameters: dict[SWLN, Ingredient],
                       scope: dict[SWLN, Ingredient], get_input: InputFun,
                       output: OutputFun, error: ErrorFun) -> None | Ingredient:
    match statement:
        case [InterpreterBase.BEGIN_DEF, sub_statement1, *sub_statements]:
            last_return = evaluate_statement(sub_statement1, me, classes,
                                             parameters, scope, get_input,
                                             output, error)
            if last_return != None:
                return last_return
            for sub_statement in sub_statements:
                last_return = evaluate_statement(sub_statement, me, classes,
                                                 parameters, scope, get_input,
                                                 output, error)
                if last_return != None:
                    return last_return
            return last_return
        case [InterpreterBase.CALL_DEF, InterpreterBase.ME_DEF, method,
              *arguments] if isSWLN(method):
            try:
                signature_brew = me.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Could not find method: {InterpreterBase.ME_DEF}."
                      f"{method}",
                      method.line_num)
            try:
                return signature_brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                         scope, error)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {obj}."
                      f"{method}",
                      statement[0].line_num)
        case [InterpreterBase.CALL_DEF, obj, method, *arguments] \
                if isSWLN(obj) and isSWLN(method):
            try:
                cuppa = scope[obj].value
            except KeyError:
                error(ErrorType.NAME_ERROR, f"Could not find object: {obj}",
                      obj.line_num)
            if cuppa == None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr: {obj}",
                      obj.line_num)
            try:
                brew = cuppa.methods[method]
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Could not find method: {obj}.{method}",
                      method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR, f"Not an object: {obj}",
                      obj.line_num)
            try:
                return brew.call(
                    *(evaluate_expression(argument, me, classes, parameters,
                                         scope, error)
                      for argument in arguments),
                    classes=classes
                )
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                      f"Method called with wrong number of arguments: {obj}."
                      f"{method}",
                      statement[0].line_num)
        case [InterpreterBase.IF_DEF, expression, true_statement]:
            condition = evaluate_expression(expression, me, classes, parameters,
                                            scope, error).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                return evaluate_statement(true_statement, me, classes,
                                          parameters, scope, get_input, output,
                                          error)
        case [InterpreterBase.IF_DEF, expression, true_statement,
              false_statement]:
            condition = evaluate_expression(expression, me, classes, parameters,
                                            scope, error).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                return evaluate_statement(true_statement, me, classes,
                                          parameters, scope, get_input, output,
                                          error)
            else:
                return evaluate_statement(false_statement, me, classes,
                                          parameters, scope, get_input, output,
                                          error)
        case [InterpreterBase.INPUT_INT_DEF, variable] if isSWLN(variable):
            if variable in parameters:
                parameters[variable] = Ingredient(int(get_input()), error)
            elif variable in scope:
                scope[variable] = Ingredient(int(get_input()), error)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.INPUT_STRING_DEF, variable] if isSWLN(variable):
            if variable in parameters:
                parameters[variable] = Ingredient(str(get_input()), error)
            elif variable in scope:
                scope[variable] = Ingredient(str(get_input()), error)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.PRINT_DEF, *arguments]:
            output(
                ''.join(
                    str(
                        evaluate_expression(argument, me, classes, parameters,
                                            scope, error)
                    )
                    for argument in arguments
                )
            )
        case [InterpreterBase.RETURN_DEF]:
            return
        case [InterpreterBase.RETURN_DEF, expression]:
            return evaluate_expression(expression, me, classes, parameters,
                                       scope, error)
        case [InterpreterBase.SET_DEF, variable, expression] \
                if isSWLN(variable):
            if variable in parameters:
                parameters[variable] = evaluate_expression(expression, me,
                                                           classes, parameters,
                                                           scope, error)
            elif variable in scope:
                scope[variable] = evaluate_expression(expression, me, classes,
                                                      parameters, scope, error)
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
        case [InterpreterBase.WHILE_DEF, expression, statement_to_run]:
            while True:
                condition = evaluate_expression(expression, me, classes,
                                                parameters, scope, error).value
                if type(condition) != bool:
                    error(ErrorType.TYPE_ERROR,
                          "Condition did not evaluate to boolean",
                          statement[0].line_num)
                if not condition:
                    break
                last_return = evaluate_statement(statement_to_run, me, classes,
                                                 parameters, scope, get_input,
                                                 output, error)
                if last_return != None:
                    return last_return
        case _:
            error(ErrorType.SYNTAX_ERROR, f"Not a valid statement: {statement}")


def main():
    interpreter = Interpreter()
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
    interpreter.run(script.splitlines())


if __name__ == '__main__':
    main()
