import concurrent.futures
import re
from itertools import repeat

import pycountry

from card_set import CardSet
from flash_card import FlashCard
from utils import Utils


class CardSetGenerator:
    """Generator for card sets.

    Uses `CardSet` and `FlashCard` classes to create new card set.
    """

    def __init__(self) -> None:
        self._utils = Utils()

    def create(self,
               path: str,
               word_col: int = 0,
               frequency_col: int = 1,
               cutoff: int = 1000,
               target_language: str = "de",
               source_language: str = "en",
               sep: str = None,
               header: int = None,
               encoding="utf-8") -> CardSet:
        """Create card set from frequency word list (FWL).

        Args:
            path (str): Path/URL to FWL, expects CSV format.
            word_col (int, optional): FWL word column. Defaults to 0.
            frequency_col (int, optional): FWL frequency column. Defaults to 1.
            cutoff (int, optional): Number of words used from FWL. Defaults to 1000.
            target_language (str, optional): Input language (ISO-639-1-Code).
                Defaults to "de".
            source_language (str, optional): Target language (ISO-639-1-Code).
                Defaults to "en".
            sep (str, optional): FWL seperator. If set to None, delimiter will be
                automatically detected. Defaults to None.
            header (int, optional): Skip header row. Defaults to None.
            encoding (str, optional): File encoding. Defaults to "utf-8".
        """
        card_set = CardSet()
        words = self._utils.get_frequency_words(path,
                                                word_col,
                                                frequency_col,
                                                cutoff,
                                                sep=sep,
                                                header=header,
                                                encoding=encoding)

        for lang in [source_language, target_language]:
            if not re.match("^[a-z]{2}$", lang) and lang != "auto":
                raise ValueError("Only ISO-639-1 codes are supported.")

        if words:
            if source_language == "en":
                words = self._remove_contraction_leftovers(words)

            # Get language from ISO-639-1-Code and preserve it
            card_set.source_lang = pycountry.languages.get(
                alpha_2=source_language).name
            card_set.target_lang = pycountry.languages.get(
                alpha_2=target_language).name

            with concurrent.futures.ThreadPoolExecutor() as executor:
                translations = executor.map(self._utils.translate, words,
                                            repeat(source_language),
                                            repeat(target_language))
                # Create card set
                for word, translation in zip(words, translations):
                    card_set.add(FlashCard(word, translation))

        return card_set

    @staticmethod
    def _remove_contraction_leftovers(words: list[str]) -> list[str]:
        """Remove contraction leftovers within given list.

        Args:
            words (list[str]): Word list.

        Returns:
            list[str]: Filtered word list.
        """

        contractions = {
            "ain't": "am not / are not / is not / has not / have not",
            "aren't": "are not / am not",
            "can't": "cannot",
            "can't've": "cannot have",
            "'cause": "because",
            "could've": "could have",
            "couldn't": "could not",
            "couldn't've": "could not have",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hadn't've": "had not have",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he had / he would",
            "he'd've": "he would have",
            "he'll": "he shall / he will",
            "he'll've": "he shall have / he will have",
            "he's": "he has / he is",
            "how'd": "how did",
            "how'd'y": "how do you",
            "how'll": "how will",
            "how's": "how has / how is / how does",
            "I'd": "I had / I would",
            "I'd've": "I would have",
            "I'll": "I shall / I will",
            "I'll've": "I shall have / I will have",
            "I'm": "I am",
            "I've": "I have",
            "isn't": "is not",
            "it'd": "it had / it would",
            "it'd've": "it would have",
            "it'll": "it shall / it will",
            "it'll've": "it shall have / it will have",
            "it's": "it has / it is",
            "let's": "let us",
            "ma'am": "madam",
            "mayn't": "may not",
            "might've": "might have",
            "mightn't": "might not",
            "mightn't've": "might not have",
            "must've": "must have",
            "mustn't": "must not",
            "mustn't've": "must not have",
            "needn't": "need not",
            "needn't've": "need not have",
            "o'clock": "of the clock",
            "oughtn't": "ought not",
            "oughtn't've": "ought not have",
            "shan't": "shall not",
            "sha'n't": "shall not",
            "shan't've": "shall not have",
            "she'd": "she had / she would",
            "she'd've": "she would have",
            "she'll": "she shall / she will",
            "she'll've": "she shall have / she will have",
            "she's": "she has / she is",
            "should've": "should have",
            "shouldn't": "should not",
            "shouldn't've": "should not have",
            "so've": "so have",
            "so's": "so as / so is",
            "that'd": "that would / that had",
            "that'd've": "that would have",
            "that's": "that has / that is",
            "there'd": "there had / there would",
            "there'd've": "there would have",
            "there's": "there has / there is",
            "they'd": "they had / they would",
            "they'd've": "they would have",
            "they'll": "they shall / they will",
            "they'll've": "they shall have / they will have",
            "they're": "they are",
            "they've": "they have",
            "to've": "to have",
            "wasn't": "was not",
            "we'd": "we had / we would",
            "we'd've": "we would have",
            "we'll": "we will",
            "we'll've": "we will have",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what shall / what will",
            "what'll've": "what shall have / what will have",
            "what're": "what are",
            "what's": "what has / what is",
            "what've": "what have",
            "when's": "when has / when is",
            "when've": "when have",
            "where'd": "where did",
            "where's": "where has / where is",
            "where've": "where have",
            "who'll": "who shall / who will",
            "who'll've": "who shall have / who will have",
            "who's": "who has / who is",
            "who've": "who have",
            "why's": "why has / why is",
            "why've": "why have",
            "will've": "will have",
            "won't": "will not",
            "won't've": "will not have",
            "would've": "would have",
            "wouldn't": "would not",
            "wouldn't've": "would not have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
            "y'all're": "you all are",
            "y'all've": "you all have",
            "you'd": "you had / you would",
            "you'd've": "you would have",
            "you'll": "you shall / you will",
            "you'll've": "you shall have / you will have",
            "you're": "you are",
            "you've": "you have"
        }

        exceptions = [
            'it', 'would', 'could', 'that', 'won', 'must', 'who', 'why',
            'should', 'he', 'I', 'where', 'will', 'might', 'there', 'they',
            'to', 'when', 'so', 'can', 'we', 'let', 'you', 'she', 'how', 'what'
        ]

        # generate filter list from contraction dict entries
        filter_list = [
            string if idx == 0 else "'" + string for key in contractions
            for idx, string in enumerate(key.split("'"))
        ]

        # remove exceptions and possible empty strings
        filter_list = list({
            entry
            for entry in filter_list if entry not in exceptions and entry != ""
        })

        return [word for word in words if word not in list(set(filter_list))]
