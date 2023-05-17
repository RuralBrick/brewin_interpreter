import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)
    
    def test_example(self):
        brewin = string_to_program('''
            (class person
  (field string name "jane")
  (method void set_name ((string n)) (set name n))
  (method string get_name () (return name))
)

(class student inherits person
  (field int beers 3)
  (method void set_beers ((int g)) (set beers g))
  (method int get_beers () (return beers))
)

(class main
  (field student s null)
  (method void main ()
    (begin
      (set s (new student))
      (print (call s get_name) " has " (call s get_beers) " beers")
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output[0], 'jane has 3 beers')
