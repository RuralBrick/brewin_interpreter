import unittest

from .settings import PURPOSELY_DIFFERENT
from bparser import string_to_program
from intbase import ErrorType
from interpreterv1 import Interpreter


class TestDefinitions(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_no_main(self):
        brewin = string_to_program('')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, _ = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)

    def test_no_method(self):
        brewin = string_to_program('(class sumn) (class main (method main () (print "main")))')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'main')

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

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()

        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 4)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_main_parameter(self):
        brewin = string_to_program('''
            (class main
                (method main (argv) (print "main"))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, _ = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)

    def test_example(self):
        brewin = string_to_program('''
            (class person
                (field name "")
                (field age 0)
                (method init (n a)
                    (begin
                    (set name n)
                    (set age a)
                    )
                )
                (method talk (to_whom)
                    (print name " says hello to " to_whom)
                )
            )

            (class main
                (field p null)
                (method tell_joke (to_whom)
                    (print "Hey " to_whom ", knock knock!")
                )
                (method main ()
                    (begin
                        (call me tell_joke "Matt") # call tell_joke in current object
                        (set p (new person))  # allocate a new person obj, point p at it
                        (call p init "Siddarth" 25) # call init in object pointed to by p
                        (call p talk "Paul")       # call talk in object pointed to by p
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'Hey Matt, knock knock!')
        self.assertEqual(output[1], 'Siddarth says hello to Paul')


class TestFields(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_out_of_order(self):
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

    def test_reassignment(self):
        brewin = string_to_program('''
            (class main
                (field greeting "hi")
                (method main ()
                    (begin
                        (set greeting 14)
                        (print greeting)
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '14')

    def test_no_initial_value(self):
        brewin = string_to_program('''
            (class main
                (field blank)
                (method main () (print "main"))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_duplicate(self):
        brewin = string_to_program('''
            (class main
                (field thing 1)
                (field thing 2)
                (method main () (print "main"))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)

    def test_field_named_const(self):
        brewin = string_to_program('''
            (class main
                (field true 1)
                (method main ()
                    (print true)
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '1')

    def test_expression_as_value(self):
        brewin = string_to_program('''
            (class main
                (field start (+ 1 2))
                (method main ()
                    (begin
                        (print start)
                    )
                )
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)


class TestMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_missing(self):
        brewin = string_to_program('(class sumn) (class main (method main () ()))')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_no_parameters(self):
        brewin = string_to_program('''
            (class main
                (method void)
                (method main () (print "main"))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_no_statement(self):
        brewin = string_to_program('''
            (class main
                (method void () )
                (method main () (print "main"))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_parameter_missing_parenthesis(self):
        brewin = string_to_program('''
            (class main
                (method void hi (return hi))
                (method main () (print (call me void "hi")))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_statement_missing_parenthesis(self):
        brewin = string_to_program('''
            (class main
                (method void (hi) return hi)
                (method main () (print (call me void "hi")))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_get_value_from_void_method(self):
        brewin = string_to_program('''
            (class main
                (method bird () ())
                (method main () (print (call me bird)))
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_get_value_from_print_method(self):
        brewin = string_to_program('''
            (class main
                (method telepath () (print ""))
                (method main () (print (call me telepath)))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'None')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_get_value_from_begin_method(self):
        brewin = string_to_program('''
            (class main
                (field status "it's so over")
                (method bird ()
                    (begin
                    (print "")
                    (set status "ballin")
                    )
                )
                (method main () (print (call me bird)))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'None')

    def test_shadowing(self):
        brewin = string_to_program('''
            (class main
                (field x 10)
                (method bar (x) (print x))  # prints 5
                (method main () (call me bar 5))
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '5')

    def test_duplicate(self):
        brewin = string_to_program('''
            (class main
                (method bird () (return "bush"))
                (method bird () (return "bush"))
                (method main () (print "main"))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)

    def test_call_to_undefined(self):
        brewin = string_to_program('''
            (class main
                (method main () (call me i_dunno))
            )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 2)

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

    def test_no_statement_body(self):
        brewin = string_to_program('''
            (class main
                (method main () ())
            )
        ''')
        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

    def test_example(self):
        brewin = string_to_program('''
            (class person
                (field name "")
                (field age 0)
                (method init (n a) (begin (set name n) (set age a)))
                (method talk (to_whom) (print name " says hello to " to_whom))
                (method get_age () (return age))
            )

            (class main
                (field p null)
                (method tell_joke (to_whom) (print "Hey " to_whom ", knock knock!"))
                (method main ()
                    (begin
                        (call me tell_joke "Leia")  # calling method in the current obj
                        (set p (new person))
                        (call p init "Siddarth" 25)  # calling method in other object
                        (call p talk "Boyan")        # calling method in other object
                        (print "Siddarth's age is " (call p get_age))
                    )
                )
            )
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'Hey Leia, knock knock!')
        self.assertEqual(output[1], 'Siddarth says hello to Boyan')
        self.assertEqual(output[2], 'Siddarth\'s age is 25')
