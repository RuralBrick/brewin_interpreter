import unittest

from .settings import PURPOSELY_DIFFERENT
from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestClasses(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_undefined(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (call (new c) m)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_duplicate(self):
        brewin = string_to_program('''
            (class c
  (method void m () (return))
)

(class c
  (method void m () (return))
)

(class main
  (method void main ()
    (call (new c) m)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 5)

    def test_named_primitive(self):
        brewin = string_to_program('''
            (class int
  (method string do () (return "brokey"))
)

(class main
    (method void main ()
      (print (call (new int) do))
    )
  )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''brokey'''.splitlines())


class TestMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_print_void(self):
        brewin = string_to_program('''
            (class c
  (method void m () (return))
)

(class main
  (method void main ()
    (print (call (new c) m))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''None'''.splitlines())

    def test_duplicate_parameter(self):
        brewin = string_to_program('''
            (class main
  (method int test ((int x) (int x)) (return (+ x x)))
    (method void main ()
      (print (call me test 9 10))
    )
  )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 2)


class TestWhile(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        interpreter = Interpreter(False, inp=['5'])
        brewin = string_to_program('''
            (class main
                (field int x 0)
                (method void main ()
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
                (field int x 0)
                (method void main ()
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
                (field int x 0)
                (method void main ()
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
                (field int x 0)
                (method void main ()
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
                (field int x 0)
                (method void main ()
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
                (field int x 0)
                (method void main ()
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
                (field int num 0)
                (field int result 1)
                (method void main ()
                    (begin
                        (print "Enter a number: ")
                        (inputi num)
                        (print num " factorial is " (call me factorial num))))

                (method int factorial ((int n))
                    (begin
                    (set result 1)
                    (while (+ "n" "0")
                        (begin
                            (set result (* n result))
                            (set n (- n 1))))
                        (return result))))
        ''')

        self.assertRaises(RuntimeError, interpreter.run, brewin)

        error_type, error_line = interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_calculator(self):
        interpreter = Interpreter(False, inp=['8', 'y', '4', 'y', '/', 'y', 'y', 'stop'])
        brewin = string_to_program('''
            (class main
                (field int a 0)
                (field int b 0)
                (field int c 0)
                (field string o "")
                (field string state "a")
                (field string in "")
                (method void main ()
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

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_condition_change_type(self):
        brewin = string_to_program('''
            (class main
                (field int state 1)
                (method bool cond ()
                    (begin
                        (set state (% (+ state 1) 2))
                        (if (== state 0)
                            (return true)
                            (return "true")
                        )
                    )
                )
                (method void main ()
                    (while (call me cond)
                        (print "hi")
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 7)

    def test_immediate_return(self):
        brewin = string_to_program('''
            (class main
                (method int main ()
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
