import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv3 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example1(self):
        brewin = string_to_program('''
            (tclass my_generic_class (field_type)
  (method void do_your_thing ((field_type x)) (call x talk))
)

(class duck
 (method void talk () (print "quack"))
)

(class person
 (method void talk () (print "hello"))
)

(class main
  (method void main ()
    (let ((my_generic_class@duck x null)
          (my_generic_class@person y null))
      # create a my_generic_class object that works with ducks
      (set x (new my_generic_class@duck))
      # create a my_generic_class object that works with persons
      (set y (new my_generic_class@person))
      (call x do_your_thing (new duck))
      (call y do_your_thing (new person))
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''quack
hello'''.splitlines())

    def test_example2(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class Square
  (field int side 10)
  (method int get_area () (return (* side side)))
)

(class Dog
  (field string name "koda")
  (method string get_name () (return name))
)

(class main
  (method void main ()
    (let ((Square s) (Dog d) (MyTemplatedClass@Square@Dog t))
      (set s (new Square))
      (set d (new Dog))
      (set t (new MyTemplatedClass@Square@Dog))
      (call t act s d)
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''Shape's area: 100
Animal's name: koda'''.splitlines())

    def test_runtime_incompatible(self):
        brewin = string_to_program('''
            (tclass Foo (field_type)
  (method void chatter ((field_type x))
    (call x quack)         # line A
  )
  (method bool compare_to_5 ((field_type x))
    (return (== x 5))
  )
)

(class Duck
 (method void quack () (print "quack"))
)

      (class main
        (field Foo@Duck t1)
        (field Foo@int t2)
        (method void main ()
          (begin
             (set t1 (new Foo@Duck))	# works fine
             (set t2 (new Foo@int))		# works fine

             (call t1 chatter (new Duck))	# works fine - ducks can talk
             (call t2 compare_to_5 5)  	# works fine - ints can be compared
             (call t1 chatter 10)  # generates a NAME ERROR on line A
          )
        )
      )

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 24)

    def test_incompatible(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass@int@string ref)
  (method void main ()
    (set ref (new MyTemplatedClass@string@bool))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 15)

    def test_compare_incompatible(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass@int@string ref1)
  (field MyTemplatedClass@string@bool ref2)
  (method void main ()
    (print (== ref1 ref2))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 16)

    def test_invalid_argument(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass@tsring@bool ref)
  (method void main ()
    (print ref)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_compare_null(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass@int@string ref)
  (method void main ()
    (print (== ref null))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output, '''true'''.splitlines())

    def test_no_arguments(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass a)		# missing both parameterized types
  (method void main ()
    (print a)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_less_arguments(self):
        brewin = string_to_program('''
            (tclass MyTemplatedClass (shape_type animal_type)
  (field shape_type some_shape)
  (field animal_type some_animal)
  	  (method void act ((shape_type s) (animal_type a))
          (begin
            (print "Shape's area: " (call s get_area))
            (print "Animal's name: " (call a get_name))
          )
        )
      )

(class main
  (field MyTemplatedClass@int a)	# missing the second parameterized type
  (method void main ()
    (print a)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 13)

    def test_unmatched_method(self):
        brewin = string_to_program('''
            (tclass Foo (field_type)
  (method void chatter ((field_type x))
    (call x quack)))

(class Duck
  (method void quack ()
    (print "quack")))
(class main
  (field Foo@Duck t1)
    (method void main ()
      (begin
        (set t1 (new Foo@Duck))
        (call t1 chatter 5) #generates a name error
)))
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 13)

    def test_int_method(self):
        brewin = string_to_program('''
            (tclass Foo (field_type)
  (method void chatter ((field_type x))
    (call x quack))) #error generated here

(class Duck
  (method void quack ()
    (print "quack")))
(class main
  (field Foo@Duck t1)
    (method void main ()
      (begin
        (set t1 (new Foo@int)) #changed type of t1
        (call t1 chatter 5)
#generates a type error, mismatch between Foo@Duck and Foo@int
)))
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 12)

    def test_add_incompatible(self):
        brewin = string_to_program('''
            (tclass Foo (field_type)
  (method void compare_to_5 ((field_type x))
    (return (== x 5)) #== operator applied to two incompatible types
  )
)

(class Duck
  (method void quack ()
    (print "quack")))
(class main
  (field Foo@Duck t1)
    (method void main ()
      (begin
        (set t1 (new Foo@Duck))
        (call t1 compare_to_5 (new Duck)) #type error generated
)))
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_bad_argument(self):
        brewin = string_to_program('''
            (tclass temp (first)
  (method first give () (return))
)

(class main
  (method void main()
    (print (new temp@est))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 7)
