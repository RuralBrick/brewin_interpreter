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
