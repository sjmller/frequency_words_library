import csv
import re
import urllib

import pandas as pd
import requests


class Utils:
    """This class contains a number of utilities."""

    def __init__(self) -> None:
        pass

    def get_frequency_words(self,
                            path: str,
                            word_col: int,
                            frequency_col: int,
                            cutoff: int,
                            sep: str = None,
                            header: int = None,
                            encoding: str = "utf-8") -> list:
        """Generate frequency word list (FWL) from provided URL.

        Args:
            path (str): Path/URL to FWL, expects CSV format.
            word_col (int): FWL word column.
            frequency_col (int): FWL frequency column.
            cutoff (int): Number of words used from FWL.
            sep (str, optional): FWL seperator. If set to None, delimiter will be
                automatically detected. Defaults to None.
            header (int, optional): Skip header row. Defaults to None.
            encoding (str, optional): File encoding. Defaults to "utf-8".

        Raises:
            TypeError: If `path` or `encoding` not of type `str`
            TypeError: If `cutoff`, `word_col` or `frequency_col` not
                of type `int`
            TypeError: If `header` not of type `int`
            TypeError: If `sep` not of type `str`

        Returns:
            list: List of all words until cutoff. Returns empty list,
                if `path` not reachable.
        """

        for entry in [path, encoding]:
            if not isinstance(entry, str):
                raise TypeError(f"<{entry}> must be of type <str>")

        for entry in [cutoff, word_col, frequency_col]:
            if not isinstance(entry, int):
                raise TypeError(f"<{entry}> must be of type <int>")

        if header is not None and not isinstance(header, int):
            raise TypeError(f"<{header}> must be of type <int>")

        if sep is not None and not isinstance(sep, str):
            raise TypeError(f"<{sep}> must be of type <str>")

        try:
            data = pd.read_csv(path,
                               sep=None,
                               header=header,
                               usecols=[word_col, frequency_col],
                               names=["word", "frequency"],
                               engine="python" if sep is None else "c")
            # Sort by frequency
            sorted_data = data.sort_values("frequency",
                                           axis=0,
                                           ascending=False)
            word_list = sorted_data["word"].to_list()[:cutoff]

        except urllib.error.URLError:
            self.print_user_info(f"Could not download data from <{path}>.",
                                 "error")
            word_list = []

        except FileNotFoundError:
            self.print_user_info(f"Provided file path <{path}> not found.",
                                 "error")
            word_list = []

        except csv.Error:
            self.print_user_info(f"Coudn't determine delimiter for <{path}>.",
                                 "error")
            word_list = []

        return word_list

    @staticmethod
    def translate(text: str,
                  source_lang: str = "auto",
                  target_lang: str = "de") -> str:
        """Translate given string using Google Translate web service.

        Args:
            text (str): String to translate.
            source_language (str, optional): Input language (ISO-639-1-Code).
                Defaults to "auto".
            target_language (str, optional): Target language (ISO-639-1-Code).
                Defaults to "de".

        Raises:
            TypeError: If `text`, `source_lang` or `target_lang` not of
                type `str`
            ValueError: if `source_lang` or `target_lang` don't comply to
                (ISO-639-1-Code) format

        Returns:
            str: Translation
        """
        for item in [text, source_lang, target_lang]:
            if not isinstance(item, str):
                raise TypeError
        for lang in [source_lang, target_lang]:
            if not re.match("^[a-z]{2}$", lang) and lang != "auto":
                raise ValueError("Only ISO-639-1 codes are supported.")

        # Google web service, might change in the future
        url = f'https://translate.google.com/m?tl={target_lang}&sl={source_lang}&q={text}'

        # Translate provided text
        content = requests.get(url, timeout=10).text

        # Check result-container and grab the content
        matches = re.findall(
            r'(?:<div class="result-container">)(.*?)(?:</div>)', content)
        result = matches[0]

        return result

    @staticmethod
    def print_user_info(msg: str, level: str) -> None:
        """Generate user info string.

        Args:
            msg (str): User information.
            level (str): Level, e.g. debug

        Raises:
            TypeError: If `msg` or `level` not of type `str`

        Returns:
            str: Formatted string, e.g. <[LEVEL] User info>
        """
        for entry in [msg, level]:
            if not isinstance(entry, str):
                raise TypeError(f"{entry} must be of type <str>")

        print(f"[{level.upper()}] {msg}")
