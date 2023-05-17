import unittest

from .settings import PURPOSELY_DIFFERENT
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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_no_statements(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (begin

                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)

        self.assertEqual(self.deaf_interpreter.get_output(), [])

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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_bad_object(self):
        brewin = string_to_program('''
            (class main
                (method main () (call uhh))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 2)

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

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 2)

    def test_null_object(self):
        brewin = string_to_program('''
            (class main
                (method main () (call null frank))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.FAULT_ERROR)
        self.assertEqual(error_line, 2)

    def test_null_object2(self):
        brewin = string_to_program('''
            (class main
                (field blank null)
                (method main () (call blank frank))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.FAULT_ERROR)
        self.assertEqual(error_line, 3)

    def test_too_many_arguments(self):
        brewin = string_to_program('''
            (class main
                (method const () (return 0))
                (method main () (print (call me const 1)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_too_few_arguments(self):
        brewin = string_to_program('''
            (class main
                (method ignorant (not_this nor_this) (return 0))
                (method main () (print (call me ignorant 1)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_multiline_too_few_arguments(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field num 0)
                (field result 1)
                (field waagabaaga null)
                (method
                main
                ()
                    (begin
                        (print "Enter a number: ")
                        (inputi num)
                        (set waagabaaga (new main))
                        (print num " factorial is " (call
                        waagabaaga
                        factorial
                        num))))

                (method
                factorial
                (n m)
                    (begin
                        (set result 1)
                        (while (> n 0)
                            (begin
                                (set result (* n result))
                                (set n (- n 1))))
                        (return result))))
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 12)

    def test_call_on_non_object(self):
        brewin = string_to_program('''
            (class main
                (field num 1)
                (method main ()
                    (begin
                        (call num do_something)
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_multiline_bad_method(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field num 0)
                (field result 1)
                (method
                main
                ()
                    (begin
                        (print "Enter a number: ")
                        (inputi num)
                        (print num " factorial is " (call
                        me
                        carl
                        num))))

                (method
                factorial
                (n m)
                    (begin
                        (set result 1)
                        (while (> n 0)
                            (begin
                            (set result (* n result))
                            (set n (- n 1))))
                        (return result))))
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 10)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_multiline_bad_object(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field num 0)
                (field result 1)
                (method
                main
                ()
                    (begin
                        (print "Enter a number: ")
                        (inputi num)
                        (print num " factorial is " (call
                        carl
                        factorial
                        num))))

                (method
                factorial
                (n m)
                    (begin
                        (set result 1)
                        (while (> n 0)
                            (begin
                            (set result (* n result))
                            (set n (- n 1))))
                        (return result))))
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 10)

    def test_primitive_as_object(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (field num 0)
                (field result 1)
                (field waagabaaga null)
                (method main ()
                    (begin
                        (print "Enter a number: ")
                        (inputi num)
                        (set waagabaaga (new main))
                        (print num " factorial is " (call result factorial num))))

                (method factorial (n)
                    (begin
                        (set result 1)
                        (while (> n 0)
                            (begin
                            (set result (* n result))
                            (set n (- n 1))))
                        (return result))))
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)


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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
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

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)


class TestInput(unittest.TestCase):
    def test_example(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)	# input value from user, store in x variable
                        (print "the user typed in " x)
                    )
                )
            )
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output[0], 'the user typed in 14')

    def test_string(self):
        interpreter = Interpreter(False, inp=['abc'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputs x)	# input value from user, store in x variable
                        (print "the user typed in " x)
                    )
                )
            )
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output[0], 'the user typed in abc')

    def test_invalid_input(self):
        interpreter = Interpreter(False, inp=['abc'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)	# input value from user, store in x variable
                        (print "the user typed in " x)
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_no_input(self):
        self.skipTest("No way to prevent freeze")
        interpreter = Interpreter(False, inp=[])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main () (inputi x))
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_bad_variable(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi y)	# input value from user, store in x variable
                        (print "the user typed in " x)
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 5)

    def test_expression(self):
        interpreter = Interpreter(False, inp=['4'])
        brewin = string_to_program('''
            (class main
                (method main ()
                    (begin
                        (inputi (+ 1 2))
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_not_enough_input(self):
        interpreter = Interpreter(False, inp=['8'])
        brewin = string_to_program('''
            (class main
                (field var 0)
                (method main ()
                    (begin
                        (inputi var)
                        (inputi var)
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)


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

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)

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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
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

        self.assertEqual(output[0], '-14')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_object(self):
        brewin = string_to_program('''
            (class main
                (method main()
                    (print me)
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)


class TestReturn(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
        brewin = string_to_program('''
            (class main
                (method foo (q)
                    (return (* 3 q)))   # returns the value of 3*q
                (method main ()
                    (print (call me foo 5))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '15')

    def test_example2(self):
        brewin = string_to_program('''
            (class main
                (method foo (q)
                    (while (> q 0)
                        (if (== (% q 3) 0)
                            (return q)  # immediately terminates loop and function foo
                            (set q (- q 1))
                        )
                    )
                )
                (method main ()
                    (print (call me foo 5))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '3')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_print_empty(self):
        brewin = string_to_program('''
            (class main
                (method not_really_void () (return))
                (method main ()
                    (print (call me not_really_void))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'None')

    def test_main(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (return 14)
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)

        self.assertEqual(self.deaf_interpreter.get_output(), [])


class TestSet(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        brewin = string_to_program('''
            (class person
                (field name "")
                (field age 0)
                (method init (n a) (begin (set name n) (set age a)))
                (method talk (to_whom) (print name " says hello to " to_whom))
            )

            (class main
                (field x 0)
                (method foo (q)
                    (begin
                        (set x 10)	 		# setting field to integer constant
                        (print x)
                        (set q true)			# setting parameter to boolean constant
                        (print q)
                        (set x (* x 5))		# setting field to result of expression
                        (print x)
                        (set x "foobar")		# setting field to a string constant
                        (print x)
                        (set x (new person))	# setting field to refer to new object
                        (set x null)			# setting field to null
                    )
                )
                (method main ()
                    (call me foo 5)
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '10')
        self.assertEqual(output[1], 'true')
        self.assertEqual(output[2], '50')
        self.assertEqual(output[3], 'foobar')

    def test_me(self):
        brewin = string_to_program('''
            (class person
                (field name "")
                (field age 0)
                (method init (n a) (begin (set name n) (set age a)))
                (method talk (to_whom) (print name " says hello to " to_whom))
            )

            (class main
                (field x 0)
                (method foo (q)
                    (begin
                        (set me (new person))
                        (call me init "hi" 23)
                        (call me talk "bye")
                    )
                )
                (method main ()
                    (call me foo 5)
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 12)

    def test_unknown_variable(self):
        brewin = string_to_program('''
            (class person
                (field name "")
                (field age 0)
                (method init (n a) (begin (set name n) (set age a)))
                (method talk (to_whom) (print name " says hello to " to_whom))
            )

            (class main
                (field x 0)
                (method foo (q)
                    (begin
                        (set y 1)
                    )
                )
                (method main ()
                    (call me foo 5)
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 12)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_void(self):
        brewin = string_to_program('''
            (class main
                (field a 0)
                (method foo () (print "hello world")) # does not return a value
                (method main ()
                    (set a (call me foo)) # MUST generate a TYPE_ERROR
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'hello world')

    def test_no_arguments(self):
        brewin = string_to_program('''
            (class main
                (field a 0)
                (method foo () (print "hello world")) # does not return a value
                (method main ()
                    (set)
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_no_value(self):
        brewin = string_to_program('''
            (class main
                (field a 0)
                (method foo () (print "hello world")) # does not return a value
                (method main ()
                    (set a)
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_expression_as_variable(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (begin
                        (set (+ 1 2) 3)
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)


class TestWhile(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        interpreter = Interpreter(False, inp=['5'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while (> x 0)
                            (begin
                                (print "x is " x)
                                (set x (- x 1))
                            )
                        )
                    )
                )
            )
        ''')

        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output[0], 'x is 5')
        self.assertEqual(output[1], 'x is 4')
        self.assertEqual(output[2], 'x is 3')
        self.assertEqual(output[3], 'x is 2')
        self.assertEqual(output[4], 'x is 1')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_missing_begin(self):
        interpreter = Interpreter(False, inp=['5'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while (> x 0)
                            (set x (- x 1))
                            (print "x is " x)
                        )
                    )
                )
            )
        ''')
        interpreter.run(brewin)
        self.assertEqual(interpreter.get_output(), [])

    def test_bad_condition(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while 1
                            (begin
                                (print "x is " x)
                                (set x (- x 1))
                            )
                        )
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 6)

    def test_no_condition(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while
                            (begin
                                (print "x is " x)
                                (set x (- x 1))
                            )
                        )
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_no_statement(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while (> x 0)
                        )
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_no_arguments(self):
        interpreter = Interpreter(False, inp=['14'])
        brewin = string_to_program('''
            (class main
                (field x 0)
                (method main ()
                    (begin
                        (inputi x)
                        (while
                        )
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_non_bool_condition(self):
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
                    (while (+ "n" "0")
                        (begin
                            (set result (* n result))
                            (set n (- n 1))))
                        (return result))))
        ''')
        self.assertRaises(RuntimeError, interpreter.run, brewin)

    def test_calculator(self):
        interpreter = Interpreter(False, inp=['8', 'y', '4', 'y', '/', 'y', 'y', 'stop'])
        brewin = string_to_program('''
            (class main
                (field a 0)
                (field b 0)
                (field c 0)
                (field o "")
                (field state "a")
                (field in "")
                (method main ()
                    (while (!= in "stop")
                        (begin
                            (if (== state "a")
                                (begin
                                    (print "Enter a number")
                                    (inputi a)
                                    (set state "b")
                                )
                            (if (== state "b")
                                (begin
                                    (print "Enter another number")
                                    (inputi b)
                                    (set state "o")
                                )
                            (if (== state "o")
                                (begin
                                    (print "Enter an operation")
                                    (inputs o)
                                    (set state "c")
                                )
                            (if (== state "c")
                                (begin
                                    (if (== o "+")
                                        (set c (+ a b))
                                    (if (== o "-")
                                        (set c (- a b))
                                    (if (== o "*")
                                        (set c (* a b))
                                    (if (== o "/")
                                        (set c (/ a b))
                                    ))))
                                    (set state "e")
                                )
                            (if (== state "e")
                                (begin
                                    (print a " " o " " b " = " c)
                                    (set state "a")
                                )
                            )))))
                            (print "Continue?")
                            (inputs in)
                        )
                    )
                )
            )
        ''')

        interpreter.reset()
        interpreter.run(brewin)
        output = interpreter.get_output()

        self.assertEqual(output, [
            'Enter a number',
            'Continue?',
            'Enter another number',
            'Continue?',
            'Enter an operation',
            'Continue?',
            'Continue?',
            '8 / 4 = 2',
            'Continue?'
        ])

    def test_condition_change_type(self):
        brewin = string_to_program('''
            (class main
                (field state 1)
                (method cond ()
                    (begin
                        (set state (% (+ state 1) 2))
                        (if (== state 0)
                            (return true)
                            (return "true")
                        )
                    )
                )
                (method main ()
                    (while (call me cond)
                        (print "hi")
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_immediate_return(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (while true
                        (begin
                            (print "hi")
                            (return 0)
                        )
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'hi')
