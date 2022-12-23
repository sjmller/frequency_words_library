import unittest
import sys
import os

CWD = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(CWD, '..'))

from flash_card import FlashCard
from card_set import CardSet


class TestCardSet(unittest.TestCase):

    def setUp(self) -> None:
        self.set = CardSet()
        self.card = FlashCard("word", "meaning")

    def tearDown(self) -> None:
        del self.set

    def test___str__(self):
        self.set.members = [self.card]
        self.assertEqual("['word:meaning']", str(self.set))

    def test___len__(self):
        no_of_values = 4
        self.set.members = [
            FlashCard(f"word{num}", f"meaning{num}")
            for num in range(no_of_values)
        ]
        self.assertEqual(no_of_values, len(self.set))

    def test_add(self):
        # valid input
        self.set.add(self.card)
        self.assertEqual(1, len(self.set))

        # add same card twice
        with self.assertRaises(RuntimeError):
            self.set.add(self.card)

        # invalid input
        with self.assertRaises(TypeError):
            self.set.add("test")

    def test_remove(self):
        # remove entry from set with one member
        self.set.members = [self.card]
        self.set.remove(self.card)
        self.assertEqual(0, len(self.set))

        # remove entry from set with several members
        no_of_members = 4
        self.set.members = [
            FlashCard(f"word{str(num)}", f"meaning{str(num)}")
            for num in range(no_of_members)
        ]
        self.set.members.append(self.card)
        self.set.remove(self.card)
        self.assertEqual(no_of_members, len(self.set))
        self.assertEqual(
            f"word{str(no_of_members-1)}:meaning{str(no_of_members-1)}",
            str(self.set.members[-1]))

        # remove non existing entry
        with self.assertRaises(ValueError):
            self.set.members = []
            self.set.members = [self.card, FlashCard("word2", "meaning2")]
            self.set.remove(FlashCard("word3", "meaning3"))

        # invalid input
        with self.assertRaises(TypeError):
            self.set.remove("test")

    def test_get(self):
        # valid index
        self.set.members = [self.card]
        self.assertEqual(self.set.get_card(0), self.card)

        # invalid type
        with self.assertRaises(TypeError):
            self.set.get_card("test")

        # invalid value
        with self.assertRaises(IndexError):
            self.set.get_card(1)

    def test___iter__(self):
        no_of_members = 4
        self.set.members = [
            FlashCard(f"word{str(num)}", f"meaning{str(num)}")
            for num in range(no_of_members)
        ]
        for idx, card in enumerate(self.set):
            self.assertEqual(str(card), str(self.set.members[idx]))