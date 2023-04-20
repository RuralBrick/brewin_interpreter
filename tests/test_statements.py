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

    def test_example(self):
        brewin = string_to_program('''
            (class main
                (field other null)
                (field result 0)
                (method main ()
                    (begin
                        (call me foo 10 20)   # call foo method in same object
                        (set other (new other_class))
                        (call other foo 5 6)  # call foo method in other object
                        (print "square: " (call other square 10)) # call expression
                    )
                )
                (method foo (a b)
                    (print a b)
                )
            )

            (class other_class
                (method foo (q r) (print q r))
                (method square (q) (return (* q q)))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '1020')
        self.assertEqual(output[1], '56')
        self.assertEqual(output[2], 'square: 100')

    def test_no_arguments(self):
        brewin = string_to_program('''
            (class main
                (method main () (call))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_bad_object(self):
        brewin = string_to_program('''
            (class main
                (method main () (call uhh))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.NAME_ERROR)
            self.assertEqual(error_line, 1)

    def test_no_method(self):
        brewin = string_to_program('''
            (class main
                (method main () (call me))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_bad_method(self):
        brewin = string_to_program('''
            (class main
                (method main () (call me frank))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.NAME_ERROR)
            self.assertEqual(error_line, 1)

    def test_null_object(self):
        brewin = string_to_program('''
            (class main
                (method main () (call null frank))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.FAULT_ERROR)
            self.assertEqual(error_line, 1)

    def test_too_many_arguments(self):
        brewin = string_to_program('''
            (class main
                (method const () (return 0))
                (method main () (print (call me const 1)))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.TYPE_ERROR)
            self.assertEqual(error_line, 2)

    def test_too_few_arguments(self):
        brewin = string_to_program('''
            (class main
                (method ignorant (not_this nor_this) (return 0))
                (method main () (print (call me ignorant 1)))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.TYPE_ERROR)
            self.assertEqual(error_line, 2)


class TestIf(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        interpreter = Interpreter(False, inp=['7'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)	# input value from user, store in x variable
                        (if (== 0 (% x 2))
                            (print "x is even")
                            (print "x is odd")   # else clause
                        )
                        (if (== x 7)
                            (print "lucky seven")  # no else clause in this version
                        )
                        (if true (print "that's true") (print "this won't print"))
                    )
                )
            )
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output[0], 'x is odd')
        self.assertEqual(output[1], 'lucky seven')
        self.assertEqual(output[2], 'that\'s true')

    def test_partial_return(self):
        brewin = string_to_program('''
            (class main
                (method f (x) (if x (return 1)))
                (method main () (print (call me f false)))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'None')

    def test_int_conditional(self):
        brewin = string_to_program('''
            (class main
                (method f (x) (if x (return 1)))
                (method main () (print (call me f 42)))
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.TYPE_ERROR)
            self.assertEqual(error_line, 1)


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

    def test_example(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (print "here's a result " (* 3 5) " and here's a boolean" true)
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'here\'s a result 15 and here\'s a booleantrue')

    def test_formatting(self):
        brewin = string_to_program('''
            (class main
                (method main()
                    (print "string" 14 true null)
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'string14trueNone')

    def test_negative_number(self):
        brewin = string_to_program('''
            (class main
                (method main()
                    (print (- 0 14))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(str(output[0]), '-14')

    def test_object(self):
        brewin = string_to_program('''
            (class main
                (method main()
                    (print me)
                )
            )
        ''')
        with self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin):
            error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
            self.assertIs(error_type, ErrorType.NAME_ERROR)
            self.assertEqual(error_line, 3)


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
