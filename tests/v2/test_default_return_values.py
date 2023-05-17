import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)
    
    def test_example(self):
        brewin = string_to_program('''
            (class main
  (method int value_or_zero ((int q)) 
     (begin
       (if (< q 0)
         (print "q is less than zero")
         (return q) # else case
       )
     )
   )
  (method void main ()
    (begin
      (print (call me value_or_zero 10))  # prints 10
      (print (call me value_or_zero -10)) # prints 0
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''10
q is less than zero
0'''.splitlines())