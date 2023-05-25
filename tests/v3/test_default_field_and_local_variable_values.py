import unittest

from bparser import string_to_program
from intbase import ErrorType
from interpreterv3 import Interpreter


class TestEverything(unittest.TestCase):
    def setUp(self) -> None:
        self.deaf_interpreter = Interpreter(console_output=False, inp=[], trace_output=False)

