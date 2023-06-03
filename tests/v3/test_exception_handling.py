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

    def test_return_exception(self):
        brewin = string_to_program('''
            (class main
  (method string regurgitate ()
    (try
      (throw "up")
      (return exception)
    )
  )
  (method void main ()
    (print (call me regurgitate))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''up'''.splitlines())

    def test_nested(self):
        brewin = string_to_program('''
            (class main
  (method string regurgitate ()
    (try
      (try
        (throw "u")
        (throw (+ exception "p"))
      )
      (try
        (throw exception)
        (return exception)
      )
    )
  )
  (method void main ()
    (print (call me regurgitate))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''up'''.splitlines())

    def test_return(self):
        brewin = string_to_program('''
            (class main
  (method string regurgitate ()
    (try
      (return "swallow")
      (return exception)
    )
  )
  (method void main ()
    (print (call me regurgitate))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''swallow'''.splitlines())

    def test_expression(self):
        brewin = string_to_program('''
            (class main
  (method string regurgitate ()
    (try
      (throw (+ "u" "p"))
      (return exception)
    )
  )
  (method void main ()
    (print (call me regurgitate))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''up'''.splitlines())

    def test_methods(self):
        brewin = string_to_program('''
            (class main
  (method string stomach ()
    (return "barf")
  )
  (method string toilet ((string contents))
    (begin
    (print (+ "flushing " contents))
    (return "all good")
    )
  )
  (method string regurgitate ()
    (try
      (throw (call me stomach))
      (return (call me toilet exception))
    )
  )
  (method void main ()
    (print (call me regurgitate))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''flushing barf
all good'''.splitlines())

    def test_in_and_out(self):
        brewin = string_to_program('''
            (class toilet
  (method string dump ((string contents) (bool flush))
    (if flush
      (return "all good")
      (throw contents)
    )
  )
)

(class main
  (field toilet throne)
  (method string regurgitate ()
    (try
      (throw (call throne dump "barf" false))
      (return (call throne dump exception true))
    )
  )
  (method void main ()
    (begin
    (set throne (new toilet))
    (print (call me regurgitate))
    )
  )
)
      ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''all good'''.splitlines())
