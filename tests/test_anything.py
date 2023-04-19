import unittest

from intbase import BParser, InterpreterBase
from interpreterv1 import Interpreter


class TestImport(unittest.TestCase):
    def test_new(self):
        interpreter = Interpreter()
        self.assertIsInstance(interpreter, InterpreterBase)
    
    def test_parser(self):
        status, msg = BParser.parse('((())))))))))))')
        self.assertFalse(status)
        self.assertEqual(msg, 'Extra closing parenthesis')

        status, msg = BParser.parse('((())(()()())(((())')
        self.assertFalse(status)
        self.assertEqual(msg, 'Unclosed parenthesis')

        status, tokens = BParser.parse('((())((())(()(()))))')
        self.assertTrue(status)
        self.assertEqual(tokens, [[[[]], [[[]], [[], [[]]]]]])
