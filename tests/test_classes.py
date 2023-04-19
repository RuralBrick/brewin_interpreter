import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestDefinitions(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_no_main(self):
        brewin = string_to_program('')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, _ = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.TYPE_ERROR)

    def test_no_method(self):
        brewin = string_to_program('(class sumn) (class main (method main () ()))')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)
    
    def test_out_of_order(self):
        brewin = string_to_program('''
            (class hi
                (method greet () ())
            )
            (class main
                (method main () (print "main"))
            )
            (class bye
                (method farewell () ())
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'main')

    def test_method_out_of_order(self):
        brewin = string_to_program('''
            (class main
                (method main () (print greeting))
                (field greeting "hi")
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'hi')
    
    def test_duplicate(self):
        brewin = string_to_program('''
            (class twin
                (method confuse () ())
            )
            (class twin
                (method confuse () ())
            )
            (class main
                (method main () (print "main"))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.TYPE_ERROR)
            self.assertEqual(error_line, 3)
