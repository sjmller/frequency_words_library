import os
import sys
import unittest
from io import StringIO
from unittest import mock

CWD = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(CWD, "data")
sys.path.insert(0, os.path.join(CWD, '..'))

import card_set_generator


class TestCardSetGenerator(unittest.TestCase):

    def setUp(self) -> None:
        self.generator = card_set_generator.CardSetGenerator()

    def test_create(self):
        file = os.path.join(TEST_DATA_DIR, "test_fwl.csv")

        # Valid file
        expected_results = [
            'you:Sie', 'i:ich', 'the:Die', 'to:zu', 'a:a', 'it:es', 'and:und',
            'that:das', 'of:von', 'is:ist', 'in:in', 'what:was', 'we:wir',
            'me:mich', 'this:diese', 'he:er', 'for:Pro', 'my:mein'
        ]
        card_set = self.generator.create(file, target_language="de")
        self.assertTrue(str(card_set) == str(expected_results))

        # Invalid file
        with mock.patch('sys.stdout', new=StringIO()):
            self.assertEqual(str(self.generator.create("unknownFile.txt")),
                             str([]))

        # Invalid language format
        with self.assertRaises(ValueError):
            self.generator.create(file, target_language="ger")

        with self.assertRaises(ValueError):
            self.generator.create(file, source_language="eng")

    def test__remove_contraction_leftovers(self):
        # Remove contraction leftovers
        self.assertEqual(
            self.generator._remove_contraction_leftovers(
                ["hello", "car", "isn", "'ll", "'t"]), ["hello", "car"])
