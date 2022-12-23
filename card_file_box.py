from random import choice

import numpy as np
import pandas as pd

from card_set import CardSet
from flash_card import FlashCard
from utils import Utils


class CardFileBox:
    """Represents card file box.

    Args:
        card_set (CardSet): `CardSet` class instance.
        source_lang (str): Source Language.
        target_lang (str): Target Language.
        no_of_compartments (int): Number of compartments.
        probabilities (list): Defines how probabel it is, that one
            of the compartments will be selected. Has to be the
            same length as `no_of_compartments`. Defaults to
            [0.55, 0.3, 0.1, 0.05].

    Attributes:
        compartments (list): List of all compartments, containing
            all cards, e.g. [[`FlashCard`], -> compartment 1
                             [`FlashCard`], -> compartment 2
                             [`FlashCard`]] -> compartment 3
        source_lang (str): Set by `source_lang` arg. Can only be set on init.
        target_lang (str): Set by `target_lang` arg. Can only be set on init.
        probabilites (list): Set by `probabilities` arg. Can only be set on
            init.
        current_card (FlashCard): Selected card (set be `CardFileBox.draw()`
            method). None, if no card was drawn.
    """

    def __init__(
        self,
        card_set: CardSet,
        source_lang: str,
        target_lang: str,
        no_of_compartments: int = 4,
        probabilities: list = [0.55, 0.3, 0.1, 0.05],
    ) -> None:

        self.compartments = self._register_cards(card_set, no_of_compartments)

        self._source_lang = source_lang
        self._target_lang = target_lang

        self._probabilities = probabilities
        self.current_card = None

        self._history = []
        self._current_compartment = None

    def draw_card(self) -> FlashCard:
        """Draw random card from card set.

        Selected card is stored as instance attribute `FlashCard.current_card`.

        Returns:
            FlashCard: New instance populated with pick. Returns None,
                if card set was not created.
        """

        def _get_random_compartment():
            """
            Choice is based on CardFileBox.weightings. The idea is to
            pick unknown words more often then not.
            """
            # Repeat until available category was picked
            pick = np.random.choice(a=list(range(len(self.compartments))),
                                    size=1,
                                    p=self.probabilities)

            return pick[0]

        # Make sure selected compartment is not empty
        subset = self.compartments[_get_random_compartment()]
        while not subset:
            subset = self.compartments[_get_random_compartment()]

        # Have at least 10 new words, before a previous word is selected
        card = choice(self.compartments[0])
        while card in self._history:
            card = choice(self.compartments[0])

        self._history += self._history + [card] if len(
            self._history) < 10 else [card] + self._history[1:]

        # preserve data
        self.current_card = card

        return card

    def upgrade_card(self):
        """Move current card into a higher compartment.

        In case the current card is in the highest compartment
        possible, it will remain in the current compartment.
        """
        if self.current_card and self._current_compartment:
            compartment_idx = self.compartments.index(
                self._current_compartment)
            if compartment_idx < len(self.compartments) - 1:
                # Get new compartment
                new_compartment_idx = compartment_idx + 1
                # Get card id from current compartment
                card_idx = self.compartments[compartment_idx].index(
                    self.current_card)
                # Insert current card in to new compartment
                self.compartments[new_compartment_idx].append(
                    self.current_card)
                # Remove current card from current compartment
                self.compartments[compartment_idx].pop(card_idx)
                # Update class attribute
                self._current_compartment = self.compartments[
                    new_compartment_idx]

    def downgrade_card(self):
        """Move current card into a lower compartment.

        In case the current card is in the lowest compartment
        possible, it will remain in the current compartment.
        """
        if self.current_card and self._current_compartment:
            compartment_idx = self.compartments.index(
                self._current_compartment)
            if compartment_idx > 0:  # lowest compartment possible
                # Get new compartment
                new_compartment_idx = compartment_idx - 1
                # Get card id from current compartment
                card_idx = self.compartments[compartment_idx].index(
                    self.current_card)
                # Insert current card in to new compartment
                self.compartments[new_compartment_idx].append(
                    self.current_card)
                # Remove current card from current compartment
                self.compartments[compartment_idx].pop(card_idx)
                # Update class attribute
                self._current_compartment = self.compartments[
                    new_compartment_idx]

    def load_setup(self, path: str, no_of_compartments: int = None) -> None:
        """Load previous setup from csv file.

        Args:
            path (str): Path to CSV file create by `CardFileBox.save_setup()` method.
            no_of_compartments (int, optional): Number of Compartments, overwrites
                automatically detected number of compartments. Defaults to None.
        """
        data = pd.read_csv(path)
        header = data.columns.values

        if no_of_compartments:
            self.compartments = [[] for _ in range(no_of_compartments)]
        else:  # detect automatically
            self.compartments = [[] for _ in range(
                max(int(num) for num in data[header[2]].to_list()) + 1)]

        self._source_lang = header[0]
        self._target_lang = header[1]

        for _, row in data.iterrows():
            card = FlashCard(row[header[0]], row[header[1]])
            self.compartments[row[header[2]]].append(card)

    def save_setup(self, path: str) -> None:
        """Save current card file box setup.

        Exports compartments and its cards into csv file. Can be used in
        combination with CardFileBox.load_setup() to restore previous session.

        Args:
            path (str): File path to CSV file.

        Raise:
            ValueError: If path is not valid, raised by `pandas`.
        """

        data = pd.DataFrame()

        dic = {self.source_lang: [], self.target_lang: [], "Compartment": []}
        for idx, compartment in enumerate(self.compartments):
            for card in compartment:
                dic[self.source_lang].append(card.vocabulary)
                dic[self.target_lang].append(card.definition)
                dic["Compartment"].append(idx)

        data.from_dict(dic).to_csv(path, index=False)

    def _register_cards(self, cards: CardSet, no_of_compartments: int) -> list:
        """Register card into first compartment.

        Args:
            cards (CardSet): Card set.
            no_of_compartments (int): Number of compartments.

        Returns:
            list: Compartment list.
        """
        compartments = [[] for _ in range(no_of_compartments)]

        if cards:
            compartments[0] = list(cards)

        return compartments

    @property
    def source_lang(self):
        """Getter and setter definition for `source_lang`."""
        return self._source_lang

    @source_lang.setter
    def source_lang(self, _):
        Utils.print_user_info(
            "Source language can only be set during initialization phase.",
            "info")

    @property
    def target_lang(self):
        """Getter and setter definition for `target_lang`."""
        return self._target_lang

    @target_lang.setter
    def target_lang(self, _):
        Utils.print_user_info(
            "Target language can only be set during initialization phase.",
            "info")

    @property
    def probabilities(self):
        """Getter and setter definition for `probabilities`."""
        return self._probabilities

    @probabilities.setter
    def probabilities(self, _):
        Utils.print_user_info(
            "Probabilities can only be set during initialization phase.",
            "info")