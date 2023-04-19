from intbase import InterpreterBase, ErrorType
from bparser import BParser


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def run(self, program):
        well_formed, tokens = BParser.parse(program)
        
        if not well_formed:
            super().error(ErrorType.SYNTAX_ERROR, tokens)


def main():
    raise NotImplementedError()


if __name__ == '__main__':
    main()
