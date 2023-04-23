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
                (method main () (print (((((((((((((((("main"))))))))))))))))))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_rogue_method(self):
        brewin = string_to_program('''
            (method function (x) (return (* 2 x)))
            (class main
                (method main () (print "main"))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'main')

    def test_rogue_class(self):
        brewin = string_to_program('''
            (class main
                (class helper (x) (return (* 2 x)))
                (method main () (print "main"))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'main')


class TestSemantics(unittest.TestCase):
    def test_field_and_method_with_same_name(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field main 0)
                (field result 1)
                (method main ()
                    (begin
                    (print "Enter a number: ")
                    (inputi main)
                    (print main " factorial is " (call me factorial main))))

                (method factorial (n)
                    (begin
                    (set result 1)
                    (while (> n 0)
                        (begin
                        (set result (* n result))
                        (set n (- n 1))))
                    (return result))))
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()
        
        self.assertEqual(output[0], 'Enter a number: ')
        self.assertEqual(output[1], '4 factorial is 24')


class TestExamples(unittest.TestCase):
    def test_our_first_brewin_program(self):
        interpreter = Interpreter(False, inp=['5'])
        brewin = string_to_program('''
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
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output[0], 'Enter a number: ')
        self.assertEqual(output[1], '5 factorial is 120')
