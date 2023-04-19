import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


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

# TODO: Rest of statements
