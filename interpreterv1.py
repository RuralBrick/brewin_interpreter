from typing import Callable
import copy

from intbase import InterpreterBase, ErrorType
from bparser import BParser, StringWithLineNumber as SWLN


OutputFun = Callable[[str], None]
ErrorFun = Callable[[ErrorType, str, int], None]


class Ingredient:
    """
    Field definition
    """
    def __init__(self, value: SWLN, error: ErrorFun) -> None:
        self.error = error

        match value:
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
                    self.error(ErrorType.SYNTAX_ERROR, "Invalid value",
                               value.line_num)

    def __repr__(self) -> str:
        match self.value:
            case True:
                return InterpreterBase.TRUE_DEF
            case False:
                return InterpreterBase.FALSE_DEF
            # NOTE: Maybe add None |-> null case
        return str(self.value)


def evaluate_expression(expression, scope: dict[SWLN, Ingredient],
                        error: ErrorFun):
    match expression:
        case SWLN(variable) if variable in scope:
            return scope[variable]
        case SWLN(const):
            return Ingredient(const, error)
        case [InterpreterBase.CALL_DEF, SWLN(obj), SWLN(method), *arguments]:
            # TODO: DOUBLE AND TRIPLE CHECK SCOPE!
            from sys import stderr
            print(f"Found call: {obj}.{method}({arguments})", file=stderr, flush=True)
            pass
        case [InterpreterBase.NEW_DEF, SWLN(name)]:
            # TODO
            from sys import stderr
            print(f"Found new: {name}", file=stderr, flush=True)
            pass
        case list(expr):
            # TODO: Rest of expressions
            from sys import stderr
            print(f"Found expression: {expr}", file=stderr, flush=True)
            pass
        case bad:
            # FIXME
            error(ErrorType.TYPE_ERROR, f"Something went wrong: {bad}")


def evaluate_statement(statement, scope: dict[SWLN, Ingredient],
                       output: OutputFun, error: ErrorFun):
    match statement:
        case [InterpreterBase.PRINT_DEF, *arguments]:
            output(
                ''.join(
                    str(evaluate_expression(argument, scope, error))
                    for argument in arguments
                )
            )
        case list(stmt):
            # TODO: Rest of statements
            from sys import stderr
            print(f"Found statement: {str(stmt):.47}...", file=stderr, flush=True)
            pass
        case bad:
            # FIXME
            error(ErrorType.TYPE_ERROR, f"Something went wrong: {bad}")


class Instruction:
    """
    Method definition
    """
    def __init__(self, name: SWLN, params: list[SWLN], statement: list,
                 scope: dict[SWLN, Ingredient], output: OutputFun,
                 error: ErrorFun) -> None:
        self.name = name
        self.formals = params
        self.statement = statement
        self.scope = scope
        self.output = output
        self.error = error

    def __repr__(self) -> str:
        return f'{self.name}({self.formals}) = {str(self.statement):.32}...'

    def call(self, *args: list[Ingredient]):
        """
        Throws ValueError on wrong number of arguments
        """
        parameters = {formal: actual for formal, actual
                      in zip(self.formals, args, strict=True)}

        scope = copy.copy(self.scope)
        scope.update(parameters)

        # FIXME: Double check
        # Especially for scoping issues
        return evaluate_statement(self.statement, scope, self.output,
                                  self.error)


class Recipe:
    """
    Class definition
    """
    def __init__(self, name: SWLN, body: list, output: OutputFun,
                 error: ErrorFun) -> None:
        self.name = name
        self.output = output
        self.error = error
        self.fields: dict[SWLN, Ingredient] = {}
        self.methods: dict[SWLN, Instruction] = {}

        for definition in body:
            match definition:
                case [InterpreterBase.FIELD_DEF, SWLN(name), SWLN(value)]:
                    self.add_field(name, value)
                case [InterpreterBase.METHOD_DEF, SWLN(name), list(params),
                      statement]:
                    self.add_method(name, params, statement)
                case bad:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Not a field or method: {bad}")

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
        self.methods[name] = Instruction(name, params, statement, self.fields,
                                         self.output, self.error)


class Barista(InterpreterBase):
    """
    Interpreter
    """
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.output = super().output
        self.error = super().error

    def init(self):
        self.classes: dict[SWLN, Recipe] = {}

    def add_class(self, name: SWLN, body: list):
        if name in self.classes:
            self.error(ErrorType.NAME_ERROR, f"Duplicate classes: {name}")
        self.classes[name] = Recipe(name, body, self.output, self.error)

    def run(self, program: list[str]):
        well_formed, tokens = BParser.parse(program)

        if not well_formed:
            self.error(ErrorType.SYNTAX_ERROR, tokens)

        self.init()

        for class_def in tokens:
            match class_def:
                case [InterpreterBase.CLASS_DEF, SWLN(name), *body]:
                    self.add_class(name, body)
                case bad:
                    self.error(ErrorType.SYNTAX_ERROR, f"Not a class: {bad}")

        # HACK
        from sys import stderr
        from pprint import pprint
        for item, cup in self.classes.items():
            print(item, file=stderr, flush=True)
            pprint(cup.fields, stderr)
            pprint(cup.methods, stderr)
        # end HACK

        try:
            chefs_brew = self.classes[InterpreterBase.MAIN_CLASS_DEF]
        except KeyError:
            self.error(ErrorType.TYPE_ERROR, "Main class not found")

        try:
            chefs_kiss = chefs_brew.methods[InterpreterBase.MAIN_FUNC_DEF]
        except KeyError:
            self.error(ErrorType.TYPE_ERROR, "Main method not found")

        try:
            chefs_kiss.call()
        except ValueError:
            self.error(ErrorType.TYPE_ERROR,
                       "Main method cannot accept arguments")


Interpreter = Barista


def main():
    interpreter = Interpreter()
    # script = '''
    #     (class main
    #         (field num 0)
    #         (field result 1)
    #         (method main ()
    #             (begin
    #             (print "Enter a number: ")
    #             (inputi num)
    #             (print num " factorial is " (call me factorial num))))

    #         (method factorial (n)
    #             (begin
    #             (set result 1)
    #             (while (> n 0)
    #                 (begin
    #                 (set result (* n result))
    #                 (set n (- n 1))))
    #             (return result))))
    # '''
    script = '''
        (class main
            (method main ()
                (print "Hello world")
            )
        )
    '''
    interpreter.run(script.splitlines())


if __name__ == '__main__':
    main()
