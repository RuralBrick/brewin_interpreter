import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
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

    def test_example2(self):
        brewin = string_to_program('''
            (class person
  (field string name "anonymous")
  (method void set_name ((string n)) (set name n))
  (method void say_something () (print name " says hi"))
)

(class student inherits person
  (field int student_id 0)
  (method void set_id ((int id)) (set student_id id))
  (method void say_something ()
    (begin
     (print "first")
     (call super say_something)  # calls person's say_something method
     (print "second")
    )
  )
)

(class main
  (field student s null)
  (method void main ()
    (begin
      (set s (new student))
      (call s set_name "julin")   # calls person's set_name method
(call s set_id 010123456) # calls student's set_id method
      (call s say_something)	  # calls student's say_something method
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''first
julin says hi
second'''.splitlines())

    def test_overloading(self):
        brewin = string_to_program('''
            (class foo
 (method void f ((int x)) (print x))
)
(class bar inherits foo
 (method void f ((int x) (int y)) (print x " " y))
)

(class main
 (field bar b null)
 (method void main ()
   (begin
     (set b (new bar))
     (call b f 10)  	# calls version of f defined in foo
     (call b f 10 20)   # calls version of f defined in bar
   )
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''10
10 20'''.splitlines())

    def test_many_levels(self):
        brewin = string_to_program('''
            (class organism
  (method string taxonomy () (return "Eukaryota"))
)

(class animal inherits organism
  (method string taxonomy () (return (+ (call super taxonomy) " Animalia")))
)

(class mammal inherits animal
  (method string taxonomy () (return (+ (call super taxonomy) " Mammalia")))
)

(class human inherits mammal
  (method string taxonomy () (return (+ (call super taxonomy) " Homo")))
)

(class cyborg inherits human
  (method string taxonomy () (return (+ (call super taxonomy) " Cyberneticus")))
)

(class main
  (method void main ()
    (print (call (new cyborg) taxonomy))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''Eukaryota Animalia Mammalia Homo Cyberneticus'''.splitlines())

    def test_access_private(self):
        brewin = string_to_program('''
            (class organism
  (method string taxonomy () (return "Eukaryota"))
)

(class animal inherits organism
  (method string taxonomy () (return (+ (call super taxonomy) " Animalia")))
)

(class mammal inherits animal
  (method string taxonomy () (return (+ (call super taxonomy) " Mammalia")))
)

(class human inherits mammal
  (field string genus " Homo")
  (method string taxonomy () (return (+ (call super taxonomy) genus)))
)

(class cyborg inherits human
  (method string taxonomy () (return (+ (call super taxonomy) genus)))
)

(class main
  (method void main ()
    (print (call (new cyborg) taxonomy))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 19)
