class FlashCard:
    """Represents flash card.

    Attributes:
        vocabulary (str): Vocabulary word.
        definition (str): Definition of the vocabulary word.
    """

    def __init__(self, vocabulary: str, definition: str) -> None:
        self.vocabulary = vocabulary
        self.definition = definition

    def __str__(self) -> str:
        return f"{self.vocabulary}:{self.definition}"
