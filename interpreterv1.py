from intbase import InterpreterBase, ErrorType
from bparser import BParser


class Ingredient:
    def __init__(self, value) -> None:
        match value:
            case 'null':
                self.value = None
            case 'true':
                self.value = True
            case 'false':
                self.value = False
            case str_or_int:
                # TODO: Regex
                pass


class Instruction:
    def __init__(self, params, statement) -> None:
        # TODO
        pass
    
    def call(self, *args):
        # TODO
        pass


class Recipe:
    def __init__(self, name, body) -> None:
        self.name = name
        self.fields = {}
        self.methods = {}

        for definition in body:
            match definition:
                case ['field', name, value]:
                    self.add_field(name, value)
                case ['method', name, params, statement]:
                    # TODO: Add name to methods
                    pass
                case bad:
                    super().error(ErrorType.SYNTAX_ERROR, f"Not a field or method: {bad}")

    def add_field(self, name, value):
        if name in self.fields:
            super().error(ErrorType.NAME_ERROR, f"Duplicate fields in {self.name}: {name}", name.line_num)
        self.fields[name] = Ingredient(value)

    def add_method(self, name, params, statement):
        if name in self.methods:
            super().error(ErrorType.NAME_ERROR, f"Duplicate methods in {self.name}: {name}", name.line_num)
        self.methods[name] = Instruction(params, statement)


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def init(self):
        self.classes = {}

    def add_class(self, name, body):
        if name in self.classes:
            super().error(ErrorType.NAME_ERROR, f"Duplicate classes: {name}")
        self.classes[name] = Recipe(name, body)

    def run(self, program):
        well_formed, tokens = BParser.parse(program)

        if not well_formed:
            super().error(ErrorType.SYNTAX_ERROR, tokens)

        self.init()

        for class_def in tokens:
            match class_def:
                case ['class', name, *body]:
                    self.add_class(name, body)
                case bad:
                    super().error(ErrorType.SYNTAX_ERROR, f"Not a class: {bad}")

        # TODO: Search for main.main


def main():
    interpreter = Interpreter()
    script = '''
        (class main
            (field num 0)
            (field result 1)
            (method main ()
                (begin
                (print "Enter a number: ")
                (inputi num)
                (print num " factorial is " (call me factorial num))))

            (method factorial (n)
                (begin
                (set result 1)
                (while (> n 0)
                    (begin
                    (set result (* n result))
                    (set n (- n 1))))
                (return result))))
    '''
    interpreter.run(script.splitlines())


if __name__ == '__main__':
    main()
