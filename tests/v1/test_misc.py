import unittest

from .settings import PURPOSELY_DIFFERENT
from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestSyntax(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_bad_statement(self):
        brewin = string_to_program('''
            (class main
                (method bird () ())
                (method main () (bird))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
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
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_me_field(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field me 0)
                (field result 1)
                (method
                main
                ()
                    (begin
                        (print "Enter a number: ")
                        (inputi me )
                        (print me " factorial is " (call
                        me
                        factorial
                        me ))))

                (method
                factorial
                (n)
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

    def test_factory(self):
        brewin = string_to_program('''
            (class robot
                (field gizmos 0)
                (field gadgets 0)
                (field gears 0)
                (method init (g1 g2 g3)
                    (begin
                        (set gizmos g1)
                        (set gadgets g2)
                        (set gears g3)
                    )
                )
                (method operate ()
                    (begin
                    (while (> gizmos 0)
                        (begin
                            (print "beep")
                            (set gizmos (- gizmos 1))
                        )
                    )
                    (while (> gadgets 0)
                        (begin
                            (print "boop")
                            (set gadgets (- gadgets 1))
                        )
                    )
                    (while (> gears 0)
                        (begin
                            (print "buzz")
                            (set gears (- gears 1))
                        )
                    )
                    )
                )
            )

            (class main
                (field supplies 3)
                (field workshop null)
                (field testbed null)
                (method factory (supplies)
                    (begin
                        (set workshop (new robot))
                        (call workshop init supplies supplies supplies)
                        (return workshop)
                    )
                )
                (method main ()
                    (begin
                        (call (call me factory supplies) operate)
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        for i in range(3):
            self.assertEqual(output[i], 'beep')
            self.assertEqual(output[i+3], 'boop')
            self.assertEqual(output[i+6], 'buzz')


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
