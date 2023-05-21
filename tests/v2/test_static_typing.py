import unittest

from .settings import PURPOSELY_DIFFERENT
from bparser import string_to_program
from intbase import ErrorType
from interpreterv2 import Interpreter


class TestFields(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_int(self):
        brewin = string_to_program('''
            (class main
  (field int a 1)
  (method void main ()
    (print a)
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '1')

    def test_ham(self):
        brewin = string_to_program('''
            (class main
  (field ham a 1)
  (method void main ()
    (print a)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_class(self):
        brewin = string_to_program('''
            (class livestock
  (method int get_num_legs ()
    (return 4)
  )
)

(class main
  (field livestock pig null)
  (method void main ()
    (begin
    (set pig (new livestock))
    (print (call pig get_num_legs))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '4')

    def test_linked_list(self):
        brewin = string_to_program('''
            (class Node
  (field Node next null)
  (field int value 0)
  (method Node get_next () (return next))
  (method Node set_next ((Node new_next)) (set next new_next))
  (method int get_value () (return value))
  (method void set_value ((int new_value)) (set value new_value))
)

(class main
  (field Node head null)
  (field Node tail null)
  (method void main ()
    (begin
      (set head (new Node))
      (call head set_value 2)
      (call head set_next tail)
      (set tail head)
      (set head (new Node))
      (call head set_value 1)
      (call head set_next tail)
      (set tail head)
      (while (!= tail null)
        (begin
          (print (call tail get_value))
          (set tail (call tail get_next))
        )
      )
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '1')
        self.assertEqual(output[1], '2')


class TestMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

    def test_example(self):
        brewin = string_to_program('''
            (class main
  (method string foo ((string a) (string b)) (return (+ a b)))
  (method void main ()
    (print (call me foo "Hello, " "World!"))
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'Hello, World!')

    def test_ham_parameter(self):
        brewin = string_to_program('''
            (class main
  (method int test ((ham x)) (return (+ x x)))
    (method void main ()
      (print (call me test 9))
    )
  )
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)


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

    def test_field_initialization_int(self):
        brewin = string_to_program('''
            (class main
  (field int x 52)
  (method void main ()
    (print x)
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '52')

    def test_field_initialization_class(self):
        brewin = string_to_program('''
            (class person
  (method void speak () (print "Hi!"))
)

(class main
  (field person p null)
  (method void main ()
    (begin
      (set p (new person))
      (call p speak)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'Hi!')

    def test_field_initialization_incompatible(self):
        brewin = string_to_program('''
            (class main
  (field int x "foo")
  (method void main ()
    (print x)
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 2)

    def test_assignment_int(self):
        brewin = string_to_program('''
            (class main
  (field int x 0)
(method void foo ((int param1) (int param2))
  (begin
    (set param1 param2)
    (set x param2)
  )
)

  (method void main ()
    (begin
    (call me foo 2 7)
    (print x)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '7')

    def test_assignment_class(self):
        brewin = string_to_program('''
            (class person
  (field string name "oops, the birth certificate is blank")
  (method string get_name () (return name))
  (method void set_name ((string new_name)) (set name new_name))
)

(class main
  (field person pf null)
(method void foo ((person p1) (person p2))
  (begin
    (set p1 p2)
    (set pf p2)
    (set p1 (new person))
  )
)

  (method void main ()
    (let ((person guest1 null) (person guest2 null))
    (set guest1 (new person))
    (call guest1 set_name "kevin")
    (set guest2 (new person))
    (call guest2 set_name "steve")
    (call me foo guest1 guest2)
    (print (call pf get_name))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'steve')

    def test_assignment_inherited(self):
        brewin = string_to_program('''
            (class person
  (field string name "oops, the birth certificate is blank")
  (method string get_name () (return name))
  (method void set_name ((string new_name)) (set name new_name))
)

(class student inherits person
  (method int get_gpa () (return 0))
)

(class main
(field person pf null)
(method void foo ((person p) (student s))
  (begin
    (set p s)
    (set pf p)
    (set pf s)
    (set p (new student))
  )
)


  (method void main ()
    (let ((person guest1 null) (student guest2 null))
    (set guest1 (new person))
    (call guest1 set_name "kevin")
    (set guest2 (new student))
    (call guest2 set_name "steve")
    (call me foo guest1 guest2)
    (print (call pf get_name))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'steve')

    def test_comparison_class(self):
        brewin = string_to_program('''
            (class person
  (field string name "oops, the birth certificate is blank")
  (method string get_name () (return name))
  (method void set_name ((string new_name)) (set name new_name))
)

(class student inherits person
  (method int get_gpa () (return 0))
)

(class main
(method void foo ((person p1) (person p2))
  (if (== p1 p2)
    (print "same object")
  )
)

  (method void main ()
    (let ((person guest1 null) (person guest2 null))
    (set guest1 (new person))
    (call guest1 set_name "kevin")
    (set guest2 guest1)
    (call me foo guest1 guest2)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'same object')

    def test_comparison_inherited(self):
        brewin = string_to_program('''
            (class person
  (field string name "oops, the birth certificate is blank")
  (method string get_name () (return name))
  (method void set_name ((string new_name)) (set name new_name))
)

(class student inherits person
  (method int get_gpa () (return 0))
)

(class main
(method void foo ((person ref1) (student ref2))
  (if (== ref1 ref2)   # valid if student inherits from person
    (print "same object")
  )
)

  (method void main ()
    (let ((person guest1 null) (student guest2 null))
    (set guest2 (new student))
    (call guest2 set_name "steve")
    (set guest1 guest2)
    (call guest1 set_name "kevin")
    (call me foo guest1 guest2)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'same object')

    def test_comparison_null(self):
        brewin = string_to_program('''
            (class dog
  (method void bark () (print "WOOF!"))
)

(class main
(method void foo ((dog r))
  (if (== r null)
    (print "invalid object")
  )
)

  (method void main ()
    (let ((dog pupper null))
    (call me foo pupper)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'invalid object')

    def test_assignment_obj_ref_null(self):
        brewin = string_to_program('''
            (class dog
  (method void bark () (print "WOOF!"))
)

(class main
(method void foo ((dog r))
  (set r null)
)

  (method void main ()
    (let ((dog pupper null))
    (set pupper (new dog))
    (call me foo pupper)
    (call pupper bark)
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'WOOF!')

    def test_assignment_return(self):
        brewin = string_to_program('''
            (class main
(method int returns_int () (return 5))
(method void foo ((int i))
  (begin
    (print i)
  (set i (call me returns_int))
    (print i)
  )
)

  (method void main ()
    (call me foo 17)
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '17')
        self.assertEqual(output[1], '5')

    def test_assignment_different_types(self):
        brewin = string_to_program('''
            (class main
(method void foo ((int param1) (string param2))
  (set param1 param2)
)

  (method void main ()
    (call me foo 17 "kevin")
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 3)

    def test_assignment_downcast(self):
        brewin = string_to_program('''
            (class person
  (method void speak () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class main
(method void foo ((student param1) (person param2))
  (set param1 param2)
)

  (method void main ()
    (call me foo (new student) (new person))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 11)

    def test_comparison_unrelated(self):
        brewin = string_to_program('''
            (class person
  (method void speak () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
(method void foo ((person ref1) (dog ref2))
  (if (== ref1 ref2)
    (print "same object")
  )
)

  (method void main ()
    (call me foo (new person) (new dog))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 15)

    def test_comparison_siblings(self):
        brewin = string_to_program('''
            (class person
  (method void speak () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
(method void foo ((student ref1) (professor ref2))
  (if (== ref1 ref2)
    (print "same object"))
)


  (method void main ()
    (call me foo (new student) (new professor))
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 19)

    def test_parameter_passing_int(self):
        brewin = string_to_program('''
            (class person
  (method void speak () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (field int q 30)
  (method void foo ((int x)) (print x))
  (method void main ()
    (call me foo q)
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '30')

    def test_parameter_passing_class(self):
        brewin = string_to_program('''
            (class person
(method void talk () (print "ih"))
)

(class student inherits person
(method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
(method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
(method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
(field person pers null)
(method void ask_person_to_talk ((person p)) (call p talk))
(method void main ()
  (begin
    (set pers (new person))
    (call me ask_person_to_talk pers)
  )
)
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'ih')

    def test_parameter_passing_subtype(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (field student s null)
  (method void ask_person_to_talk ((person p)) (call p talk))
  (method void main ()
    (begin
      (set s (new student))
      (call me ask_person_to_talk s)
    )
  )
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'ih')

    def test_parameter_passing_incompatible(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (field bool q true)
  (method void foo ((int x)) (print x))
  (method void main ()
    (call me foo q)
  )
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 21)

    def test_parameter_passing_unrelated(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (field person pers null)
  (method void ask_dog_to_bark ((dog d)) (call d bark))
  (method void main ()
    (begin
      (set pers (new person))
      (call me ask_dog_to_bark pers)
    )
  )
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 23)

    def test_parameter_passing_siblings(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (field student stud null)
  (method void ask_prof_to_talk ((professor p)) (call p talk))
  (method void main ()
    (begin
      (set stud (new student))
      (call me ask_prof_to_talk stud)
    )
  )
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.NAME_ERROR)
        self.assertEqual(error_line, 23)

    def test_returned_value_int(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method int foo () (return 5))
  (method void main () (print (call me foo)))
)


        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], '5')

    def test_returned_value_class(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method person foo () (return (new person)))
  (method void main () (call (call me foo) talk))
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'ih')

    def test_returned_value_upcast(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method person foo () (return (new student)))
  (method void main () (call (call me foo) talk))
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'ih')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_null(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method person foo () (return null))
  (method void main () (print (call me foo)))
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'None')

    def test_returned_value_void(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method void foo ((int q))
    (if (== q 0)
      (return)
      (print "q is non-zero")
    )
  )
  (method void main () (call me foo 5))
)

        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()

        self.assertEqual(output[0], 'q is non-zero')

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_incompatible(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method int foo () (return false))
  (method void main () (print (call me foo)))
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 18)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_unrelated(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method person foo () (return (new dog)))
  (method void main () (call me foo))
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 18)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_siblings(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method student foo () (return (new professor)))
  (method void main () (call me foo))
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 18)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_downcast(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method student foo () (return (new person)))
  (method void main () (call me foo))
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 18)

    @unittest.skipIf(PURPOSELY_DIFFERENT, "Purposely different")
    def test_returned_value_non_void(self):
        brewin = string_to_program('''
            (class person
  (method void talk () (print "ih"))
)

(class student inherits person
  (method void scream () (print "AAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH"))
)

(class professor inherits person
  (method void lecture () (print "eeeeeeeeeeeeeeeeeeeeeeeee"))
)

(class dog
  (method void run_around () (print "beliwqnflskdnlqk3rjlsijf"))
)

(class main
  (method void foo () (return 5))
  (method void main () (call me foo))
)

        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 18)

    def test_return_assign_type(self):
        brewin = string_to_program('''
            (class a
  (method int return_int () (return 5))
)

(class b inherits a
  (method int return_int () (return 6))
)

(class main
  (field b obj2 null)
  (method a get_a ()
    (return null)
  )
  (method void main ()
    (begin
      (set obj2 (call me get_a))
    )
  )
)
        ''')

        self.assertRaises(RuntimeError, self.deaf_interpreter.run, brewin)

        error_type, error_line = self.deaf_interpreter.get_error_type_and_line()
        self.assertIs(error_type, ErrorType.TYPE_ERROR)
        self.assertEqual(error_line, 16)

    def test_object_comparison1(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o1 (new person))
      (set o2 o1)
      (print (== o1 o2))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''true'''.splitlines())

    def test_object_comparison2(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o1 (new person))
      (set o2 (new person))
      (print (== o1 o2))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''false'''.splitlines())

    def test_object_comparison3(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o1 (new robot))
      (set o2 o1)
      (print (== o1 o2))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''true'''.splitlines())

    
    def test_object_comparison4(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o1 (new person))
      (set o2 (new robot))
      (print (== o1 o2))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''false'''.splitlines())

    def test_object_comparison5(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o3 (new robot))
      (set o1 o3)
      (print (== o1 o3))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''true'''.splitlines())

    def test_object_comparison6(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (set o3 (new robot))
      (set o1 (new robot))
      (print (== o1 o3))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''false'''.splitlines())

    def test_object_comparison7(self):
        brewin = string_to_program('''
            (class person
  (method void dissociate () (return))
)

(class robot inherits person
  (method void beep () (return))
)

(class main
  (field person o1 null)
  (field person o2 null)
  (field robot o3 null)
  (method void main ()
    (begin
      (print (== o1 o3))
    )
  )
)
        ''')

        self.deaf_interpreter.reset()
        self.deaf_interpreter.run(brewin)
        output = self.deaf_interpreter.get_output()
        
        self.assertEqual(output, '''true'''.splitlines())
