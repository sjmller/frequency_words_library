from flash_card import FlashCard


class CardSet:
    """Represents card set made out of `FlashCard` instances.

    Args:
        items (list, optional): List of `FlashCards` to prepopulate
            `CardSet.members` attribute. Defaults to [].

    Attributes:
        members (list): Contains all added `FlashCard` instances.
    """

    def __init__(self, items: list = None) -> None:
        self.members = items if items is not None else []

    def __len__(self) -> int:
        return len(self.members)

    def __str__(self) -> str:
        return str([str(card) for card in self.members])

    def __iter__(self):
        return CardSetIter(self)

    def add(self, card: FlashCard) -> None:
        """Add new card to set.

        Args:
            card (FlashCard): `FlashCard` instance.

        Raises:
            TypeError: If `card` not of type `FlashCard`.
            RunTimeError: If `card`is already part of the `CardSet`.
        """
        if not isinstance(card, FlashCard):
            raise TypeError(
                f"Expected input of type <class 'FlashCard'>, got {type(card)}"
            )

        if card in self.members:
            raise RuntimeError(
                f"<{card}> is already a member of this card set.")

        self.members.append(card)

    def remove(self, card: FlashCard) -> None:
        """Remove card from set.

        Args:
            card (FlashCard): `FlashCard` instance.

        Raises:
            TypeError: If `card` not of type `FlashCard`.
            ValueError: If `card` not part of `CardSet`. Raised by `list` class.
        """
        if not isinstance(card, FlashCard):
            raise TypeError(
                f"Expected input of type <class 'FlashCard'>, got {type(card)}"
            )

        self.members.remove(card)

    def get_card(self, index: int):
        """Get card from card set.

        Args:
            index (int): CardSet.members list index.

        Raises:
            TypeError: If `index` not of type `int`, raised by `list` class.
            IndexError: If `index` not part of `CardSet.members`, raised by `list` class.

        Returns:
            FlashCard: Card instance for given index.
        """
        return self.members[index]


class CardSetIter:
    """Iteration defition for `CardSet` class instance."""
    # This class is just used or iteration purposes of main class
    # pylint: disable=too-few-public-methods
    def __init__(self, card_set_class):
        self._cards = card_set_class.members
        self._class_size = len(card_set_class.members)
        self._current_index = 0

    def __next__(self):
        if self._current_index < self._class_size:
            member = self._cards[self._current_index]
            self._current_index += 1
            return member

        raise StopIteration
