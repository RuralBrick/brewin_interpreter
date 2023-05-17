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
  (method void say_something () (print name " says hi"))
)

(class student inherits person
  (method void say_something ()
    (print "Can I have a project extension?")
  )
)

(class main
  (field person p null)
  (method void foo ((person p)) # foo accepts a "person" as an argument
    (call p say_something)
  )
  (method void main ()
    (begin
      (set p (new student))  # assigns p, which is a person object ref
                             # to a student object. This is allowed!  
      (call me foo p)        # passes a "student" as an argument to foo
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output[0], 'Can I have a project extension?')
