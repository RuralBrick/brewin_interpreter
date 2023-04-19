from bparser import *
from intbase import *


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def run(self, program):
        return super().run(program)


def main():
    print(BParser.parse('((())))))))))))'))
    print(BParser.parse('((())(()()())(((())'))
    print(BParser.parse('((())((())(()(()))))'))
    print(StringWithLineNumber('saldjflaksdj', 28934).line_num)

if __name__ == '__main__':
    main()
