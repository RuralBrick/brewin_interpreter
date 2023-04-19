import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestBegin(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (print "hello")
                        (print "world")
                        (print "goodbye")
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'hello')
        self.assertEqual(output[1], 'world')
        self.assertEqual(output[2], 'goodbye')

    def test_example2(self):
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (if (== x 0)
                        (begin		# execute both print statements if x is zero
                            (print "a")
                            (print "b")
                        )
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'a')
        self.assertEqual(output[1], 'b')

    def test_no_statements(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (begin

                    )
                )
            )
        ''')
        self.deaf_interpreter.run(brewin)

    def test_no_statement_body(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (begin
                        ()
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_print(self):
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (print
                        (begin
                            (print "hello")
                            (print "world")
                            (print "goodbye")
                        )
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)


class TestCall(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish


class TestIf(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish


class TestInput(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish


class TestPrint(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_expression_missing_parenthesis(self):
        brewin = string_to_program('''
            (class main
                (method void (hi) (return hi))
                (method main () (print * 3 5))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.NAME_ERROR)
            self.assertEqual(error_line, 2)

    # TODO: Finish


class TestReturn(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish


class TestSet(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish


class TestWhile(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    # TODO: Finish
