import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv3 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
        brewin = string_to_program('''
            (class main
 (method void foo ()
   (begin
     (print "hello")
     (throw "I ran into a problem!")
     (print "goodbye")
   )
 )

 (method void bar ()
   (begin
     (print "hi")
     (call me foo)
     (print "bye")
   )
 )

 (method void main ()
  (begin
    (try
	  # try running the a statement that may generate an exception
       (call me bar)
       # only run the following statement if an exception occurs
       (print "I got this exception: " exception)
    )
    (print "this runs whether or not an exception occurs")
  )
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''hi
hello
I got this exception: I ran into a problem!
this runs whether or not an exception occurs'''.splitlines())

    def test_example2(self):
        brewin = string_to_program('''
            (class main
  (method void bar ()
     (begin
        (print "hi")
        (throw "foo")
        (print "bye")
     )
  )
  (method void main ()
    (begin
      (try
       (call me bar)
       (print "The thrown exception was: " exception)
      )
      (print "done!")
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''hi
The thrown exception was: foo
done!'''.splitlines())

    def test_out_of_scope(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (begin
      (try
       (call me bar)
       (print "The thrown exception was: " exception)
      )
      (print "This should fail: " exception)  # fails with NAME_ERROR
    )
  )
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 5)

    def test_termination(self):
        brewin = string_to_program('''
            (class main
 (method void foo ()
   (while true
     (begin
       (print "argh")
       (throw "blah")
       (print "yay!")
     )
   )
 )

 (method void bar ()
  (begin
     (print "hello")
     (call me foo)
     (print "bye")
  )
 )

 (method void main ()
   (begin
     (try
       (call me bar)
       (print exception)
     )
     (print "woot!")
   )
 )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''hello
argh
blah
woot!'''.splitlines())

    def test_non_string(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (throw 1)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_pass(self):
        brewin = string_to_program('''
            (class main
  (method void main ()
    (try
      (try
        (throw "oof")
        (throw "foo")
      )
      (print exception)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''foo'''.splitlines())

    def test_exception_expression(self):
        brewin = string_to_program('''
            (class main
  (method void main()
    (try
      (throw (+ "Hello," " World!"))
      (print exception)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''Hello, World!'''.splitlines())

    def test_nested_throws(self):
        brewin = string_to_program('''
            (class main
  (method string throws ()
    (throw "World!")
  )
  (method void main()
    (try
      (throw (+ "Hello, " (call me throws)))
      (print exception)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''World!'''.splitlines())
