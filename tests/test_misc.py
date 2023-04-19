import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestSyntax(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_bad_statement(self):
        brewin = string_to_program('''
            (class main
                (method bird () ())
                (method main () (bird))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.SYNTAX_ERROR)
            self.assertEqual(error_line, 2)

    def test_get_value_from_bad_statement(self):
        brewin = string_to_program('''
            (class main
                (field hand 0)
                (method bird () ())
                (method main () ((set hand (bird))))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_a_million_parenthesis(self):
        brewin = string_to_program('''
            (class main
                (method main () (((((((((((((((((print "main"))))))))))))))))))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)
