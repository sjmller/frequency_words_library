import unittest
import sys
import os
from io import StringIO

CWD = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(CWD, "data")
sys.path.insert(0, os.path.join(CWD, '..'))

from utils import Utils
from unittest import mock


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.tools = Utils()

    def tearDown(self) -> None:
        del self.tools

    def test_print_user_info(self):
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            self.tools.print_user_info("This is a test", "info")
            self.assertEqual("[INFO] This is a test",
                             fake_out.getvalue().strip())

        # Invalid Input
        with self.assertRaises(TypeError):
            self.tools.print_user_info(1, 2)

    def test_translate(self):
        # Single word
        self.assertEqual(
            self.tools.translate("Auto", source_lang="de", target_lang="en"),
            "automobile")
        # Sentence
        self.assertEqual(
            self.tools.translate("I'll buy a car.",
                                 source_lang="en",
                                 target_lang="de"),
            "Ich werde ein Auto kaufen.")
        # Empty string
        self.assertEqual(self.tools.translate(""), "")
        # ISO-639-1 compatible codes
        with self.assertRaises(ValueError):
            self.tools.translate("Auto", source_lang="ger", target_lang="en")
        with self.assertRaises(ValueError):
            self.tools.translate("Auto", source_lang="de", target_lang="en-us")
        # Auto language detection
        self.assertEqual(
            self.tools.translate("測試", source_lang="auto", target_lang="de"),
            "Prüfung")
        # TypeError for non-string input
        with self.assertRaises(TypeError):
            self.tools.translate(1)
        with self.assertRaises(TypeError):
            self.tools.translate("Test", 1, "en")
        with self.assertRaises(TypeError):
            self.tools.translate("Test", "de", 1)

    def test_get_frequency_words(self):
        test_fwl = os.path.join(TEST_DATA_DIR, "test_fwl.csv")
        empty_fwl = os.path.join(TEST_DATA_DIR, "empty.csv")
        fwl_with_header = os.path.join(TEST_DATA_DIR, "fwl_with_header.csv")

        # Valid File/URL
        self.assertEqual(
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5),
            ['you', 'i', 'the', 'to', 'a'])

        # Invalid File/URL
        with mock.patch('sys.stdout', new=StringIO()):
            self.assertEqual(
                self.tools.get_frequency_words("http://unknown.txt",
                                               word_col=0,
                                               frequency_col=1,
                                               cutoff=5), [])

        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            path = "http://unknown.txt"
            msg = f"[ERROR] Could not download data from <{path}>."
            self.tools.get_frequency_words(path,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5)
            self.assertEqual(msg, fake_out.getvalue().strip())

        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            path = "unknown.txt"
            msg = f"[ERROR] Provided file path <{path}> not found."
            self.tools.get_frequency_words(path,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5)
            self.assertEqual(msg, fake_out.getvalue().strip())

        # Empty file -> delimiter determination fails
        with mock.patch('sys.stdout', new=StringIO()):
            self.assertEqual(
                self.tools.get_frequency_words(empty_fwl,
                                               word_col=0,
                                               frequency_col=1,
                                               cutoff=5), [])

        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            msg = f"[ERROR] Coudn't determine delimiter for <{empty_fwl}>."
            self.tools.get_frequency_words(empty_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5)
            self.assertEqual(msg, fake_out.getvalue().strip())

        # Header skip
        self.assertEqual(
            self.tools.get_frequency_words(fwl_with_header,
                                           word_col=0,
                                           frequency_col=1,
                                           header=0,
                                           cutoff=5),
            ['you', 'i', 'the', 'to', 'a'])

        # Invalid input type for path and encoding
        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(path=1,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5)
        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5,
                                           encoding=True)

        # Invalid input type for cutoff, word_col, frequency_col
        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff="test")

        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col="test",
                                           frequency_col=1,
                                           cutoff=5)

        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col="test",
                                           cutoff=5)

        # Invalid input type for header
        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5,
                                           header="test")

        # Invalid input type for sep
        with self.assertRaises(TypeError):
            self.tools.get_frequency_words(test_fwl,
                                           word_col=0,
                                           frequency_col=1,
                                           cutoff=5,
                                           sep=True)
