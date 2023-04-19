from intbase import InterpreterBase, ErrorType


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def run(self, program):
        return super().run(program)


def main():
    raise NotImplementedError()

if __name__ == '__main__':
    main()
