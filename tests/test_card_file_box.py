import csv
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

CWD = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(CWD, "data")
sys.path.insert(0, os.path.join(CWD, '..'))

from card_file_box import CardFileBox
from card_set import CardSet
from flash_card import FlashCard


class TestCardFileBox(unittest.TestCase):

    def setUp(self) -> None:
        # self.generator = CardSetGenerator()
        self.card_set = CardSet(
            [FlashCard(f"word{num}", f"meaning{num}") for num in range(10)])
        self.box = CardFileBox(self.card_set,
                               source_lang="en",
                               target_lang="de")

    def test_draw(self):
        # Draw new card and check if it's unique
        tries = 10
        test_list = [str(self.box.draw_card()) for _ in range(tries)]
        self.assertEqual(tries, len(set(test_list)))

    def test_save_setup(self):
        test_file_path = os.path.join(
            TEST_DATA_DIR,
            f"{self.box.source_lang}-{self.box.target_lang}.csv")
        self.box.save_setup(test_file_path)

        # Check if file was created
        self.assertTrue(os.path.exists(test_file_path))

        # Check csv file
        with open(test_file_path, 'r') as file:
            csv_file = csv.DictReader(file)

            read_results = []
            for line in csv_file:
                read_results.append(":".join([
                    f"{line[self.box.source_lang]}",
                    f"{line[self.box.target_lang]}"
                ]))

        # Compare read results with data in memory
        self.assertTrue(
            read_results == [str(card) for card in self.box.compartments[0]])

        # Remove test file
        os.remove(test_file_path)

        # ValueError check
        with self.assertRaises(ValueError):
            self.box.save_setup(1)

    def test_load_setup(self):
        test_file = os.path.join(TEST_DATA_DIR, "load_setup_test.csv")
        self.box = CardFileBox(card_set=None,
                               source_lang="en",
                               target_lang="de")
        self.box.load_setup(test_file)

        # load valid file
        expected_results = [
            ["you:Sie"],  # compartment 0
            ["i:ich"],  # compartment 1
            ["the:das", "and:und"],  # compartment 2
            ["to:zu", "that:das"],  # compartment 3
            ["a:a", "of:von"],  # compartment 4
            ["it:es"]  # compartment 5
        ]

        for id_compartment, compartment in enumerate(self.box.compartments):
            for id_card, card in enumerate(compartment):
                self.assertEqual(expected_results[id_compartment][id_card],
                                 str(card))

        # overwrite number of compartments
        num = 8
        self.box.load_setup(test_file, no_of_compartments=num)
        self.assertEqual(len(self.box.compartments), num)

    def test_downgrade_card(self):
        # move first element of first compartment into fourths compartment
        self.box.compartments[-1].append(self.box.compartments[0][0])
        self.box.compartments[0].pop(0)
        # set variables manually, this is normally done by draw_card method
        self.box.current_card = self.box.compartments[-1][0]
        self.box._current_compartment = self.box.compartments[-1]
        # downgrade card serveral times, card should end up in first compartment
        for index in [2, 1, 0, 0]:  # represents expected index
            self.box.downgrade_card()
            self.assertEqual(  # check if index update is correct
                self.box.compartments.index(self.box._current_compartment),
                index)
        self.assertTrue(self.box.current_card in self.box.compartments[0])

    def test_upgrade_card(self):
        # set variables manually, this is normally done by draw_card method
        self.box.current_card = self.box.compartments[0][0]
        self.box._current_compartment = self.box.compartments[0]
        # upgrade card serveral times, card should end up in last compartment
        for index in [1, 2, 3, 3]:  # represents expected index
            self.box.upgrade_card()
            self.assertEqual(  # check if index update is correct
                self.box.compartments.index(self.box._current_compartment),
                index)
        self.assertTrue(self.box.current_card in self.box.compartments[-1])

    def test_probabilitiies(self):
        with patch('sys.stdout', new=StringIO()):
            # Make sure probabilities can't be changed during runtime
            self.box.probabilities = []
            self.assertNotEqual(self.box.probabilities, [])
            self.box.source_lang = None
            self.assertIsNotNone(self.box.source_lang)
            self.box.target_lang = None
            self.assertIsNotNone(self.box.target_lang)
