import unittest

from .settings import PURPOSELY_DIFFERENT
from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestGeneral(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_int_plus_int(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (print (+ 9 10))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '19')

    def test_int_minus_int(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (print (- 69 42))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '27')

    def test_int_times_int(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (print (* 3 5))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '15')

    def test_int_div_int(self):
        brewin = string_to_program('''
            (class main
                (method main ()
                    (print (/ 7 2))
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '3')

    def test_str_plus_int(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (+ "the meaning of life is " 42)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_int_eq_str(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (== 42 "42")))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_str_eq_bool(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (== "42" true)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_bool_eq_int(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (== true 42)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_str_sub_str(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (- "abc" "a")))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_str_or_int(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (| "fours up" 4444)))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_not_int(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (! 0)))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_cat_three(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (+ "hello " "every " "world!")))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'hello every ')

    def test_not_null(self):
        brewin = string_to_program('''
            (class main
                (method main () (print (! null)))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_pointers(self):
        brewin = string_to_program('''
            (class ob
                (method ject ()
                    (return 1)
                )
            )

            (class main
                (field object null)
                (method main ()
                    (begin
                        (print (== null null))
                        (print (== null object))
                        (print (== object null))
                        (print (== object object))
                        (print (!= null null))
                        (print (!= null object))
                        (print (!= object null))
                        (print (!= object object))
                        (set object (new ob))
                        (print (== null null))
                        (print (== null object))
                        (print (== object null))
                        (print (== object object))
                        (print (!= null null))
                        (print (!= null object))
                        (print (!= object null))
                        (print (!= object object))
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        expected = '''true
true
true
true
false
false
false
false
true
false
false
true
false
true
true
false'''

        self.assertEqual(output, expected.splitlines())

    def test_pond_scene(self):
        brewin = string_to_program('''
            (class duck
                (method speak (theres_bread)
                    (if theres_bread
                        (return "quack quack quack")
                        (return "quack")
                    )
                )
            )
            (class main
                (field pond "water")
                (method main ()
                    (begin
                        (set pond (new duck))
                        (print (+ (call pond speak true) " is heard from the pond"))
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'quack quack quack is heard from the pond')

    def test_missing_class(self):
        brewin = string_to_program('''
            (class duck
                (method speak (theres_bread)
                    (if theres_bread
                        (return "quack quack quack")
                        (return "quack")
                    )
                )
            )
            (class main
                (field pond "water")
                (method main ()
                    (begin
                        (set pond (new goose))
                        (print (+ (call pond speak true) " is heard from the pond"))
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_missing_field(self):
        brewin = string_to_program('''
            (class duck
                (method speak (theres_bread)
                    (if theres_bread
                        (return "quack quack quack")
                        (return "quack")
                    )
                )
            )
            (class main
                (field lake "water")
                (method main ()
                    (begin
                        (set pond (new duck))
                        (print (+ (call pond speak true) " is heard from the pond"))
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 13)

    def test_missing_parameter(self):
        brewin = string_to_program('''
            (class duck
                (method speak (theres_bread)
                    (if scared
                        (return "quack quack quack")
                        (return "quack")
                    )
                )
            )
            (class main
                (field pond "water")
                (method main ()
                    (begin
                        (set pond (new duck))
                        (print (+ (call pond speak true) " is heard from the pond"))
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)


class TestNew(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_out_of_order(self):
        brewin = string_to_program('''
            (class main
                (field other null)
                (method main ()
                    (begin
                    (set other (new other_class))  # HERE
                    (call other foo 5 6)
                    )
                )
                )

                (class other_class
                (field a 10)
                (method foo (q r) (print (+ a (+ q r))))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '21')

    def test_unknown_class(self):
        brewin = string_to_program('''
            (class duck
                (method speak (theres_bread)
                    (if theres_bread
                        (return "quack quack quack")
                        (return "quack")
                    )
                )
            )
            (class main
                (field pond "water")
                (method main ()
                    (begin
                        (set pond (new goose))
                        (print (+ (call pond speak true) " is heard from the pond"))
                    )
                )
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)
