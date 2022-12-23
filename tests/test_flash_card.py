import unittest
import sys
import os

CWD = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(CWD, '..'))

from flash_card import FlashCard


class TestFlashCard(unittest.TestCase):

    def test___str__(self):
        self.assertEqual("word:meaning", str(FlashCard("word", "meaning")))
