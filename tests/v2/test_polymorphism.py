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

    def test_example2(self):
        brewin = string_to_program('''
            (class person
  (field string name "jane")
  (method void say_something () (print name " says hi")
  )
)

(class student inherits person
  (method void say_something ()
    (print "Can I have an extension?")
  )
)

(class main
  (field person p null)
  (method void foo ((person p)) # foo accepts a "person" as an argument
    (call p say_something)
  )
  (method void main ()
    (begin
      (set p (new student))  # Assigns p, which is a person object ref
                             # to a student obj. This is polymorphism!
      (call me foo p)        # Passes a student object as an argument
                             # to foo. This is also polymorphism!
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''Can I have an extension?'''.splitlines())

    def test_assignment(self):
        brewin = string_to_program('''
            (class B
  (method string M () (return "base"))
)

(class D inherits B
  (method string M () (return "derived"))
)

(class DD inherits D
  (method string MM () (return "double derived"))
)

(class main
  (field B f1 null)
  (field D f2 null)
  (method void main ()
    (begin
      (set f1 (new D))
      (print (call f1 M))
      (set f2 (new DD))
      (print (call f2 M))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''derived
derived'''.splitlines())

    def test_parameters(self):
        brewin = string_to_program('''
            (class B
  (method string M () (return "base"))
)

(class D inherits B
  (method string M () (return "derived"))
)

(class DD inherits D
  (method string MM () (return "double derived"))
)

(class main
  (method string m ((B p1) (D p2)) (return (+ (call p1 M) (call p2 M))))
  (method void main ()
    (begin
      (print (call me m (new D) (new DD)))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''derivedderived'''.splitlines())

    def test_downcast(self):
        brewin = string_to_program('''
            (class B
  (method string M () (return "base"))
)

(class D inherits B
  (method string M () (return "derived"))
)

(class DD inherits D
  (method string MM () (return "double derived"))
)

(class main
  (method string m ((B p1) (D p2)) (return (+ (call p1 M) (call p2 M))))
  (method void main ()
    (begin
      (print (call me m (new D) (new B)))
    )
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 17)
