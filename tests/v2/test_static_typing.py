import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestFields(unittest.TestCase):
    pass


class TestMethods(unittest.TestCase):
    pass


class TestTypeChecking(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)
    
    def test_example(self):
        brewin = string_to_program('''
            (class main
 (method int add ((int a) (int b))
    (return (+ a b))
 )
 (field int q 5)
 (method void main ()
  (print (call me add 1000 q))
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output[0], '1005')
