import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv3 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        brewin = string_to_program('''
            (class Dog
  (method void bark () (print "WOOF"))
)

(class main
 (field Dog e)
 (method void main ()
  (let ((bool b) (string c) (int d))
    (print b)  # prints False
    (print c)  # prints empty string
    (print d)  # prints 0
    (if (!= e null) (print "value") (print "null")) # prints null
  )
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''false

0
null'''.splitlines())

    def test_mixed_optional(self):
        brewin = string_to_program('''
            (class main
  (field int x 10)	# with explicit initialization
	(field bool y)    # with default initialization
  (method void main ()
    (let ((string z "hi") (main w))
      (print x)
      (print y)
      (print z)
      (if (== w null) (print "null") (print "main"))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''10
false
hi
null'''.splitlines())
