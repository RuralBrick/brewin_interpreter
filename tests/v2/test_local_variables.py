import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
        brewin = string_to_program('''
            (class main
 (method void foo ((int x))
     (let ((int y 5) (string z "bar"))
        (print x)
        (print y)
        (print z)
     )
 )
 (method void main ()
   (call me foo 10)
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''10
5
bar'''.splitlines())

    def test_example2(self):
        brewin = string_to_program('''
            (class main
 (method void foo ((int x))
   (begin
     (print x)  					# Line #1: prints 10
     (let ((bool x true) (int y 5))
       (print x)					# Line #2: prints true
       (print y)					# Line #3: prints 5
     )
     (print x)					# Line #4: prints 10
   )
 )
 (method void main ()
   (call me foo 10)
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''10
true
5
10'''.splitlines())

    def test_out_of_scope(self):
        brewin = string_to_program('''
            (class main
 (method void foo ()
   (begin
     (let ((int y 5))
       (print y)		# this prints out 5
     )
     (print y)  # this must result in a name error - y is out of scope!
   )
 )
 (method void main ()
   (call me foo)
 )
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 7)

    def test_duplicate(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (let ((string name "") (string name ""))
      (print name)
    )
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 3)

    def test_shadowing(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (let ((string name "bro"))
      (let ((string name "sis"))
        (print name)
      )
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''sis'''.splitlines())
