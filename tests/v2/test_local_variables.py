import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)
    
    def test_example(self):
        brewin = string_to_program('''
            ((class main
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
        
        self.assertEqual(output[0], '''10
5
bar'''.splitlines())
