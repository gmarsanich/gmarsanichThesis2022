import pandas as pd
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector

"""This is a library of helper functions for the analysis"""


def detect_language(text: str) -> str:

    """This function takes a string and detects the language it's most likely written in using the SpaCy library"""

    def get_lang_detector(nlp, name):
        """Required by SpaCy"""
        return LanguageDetector()

    nlp = spacy.load("en_core_web_sm")
    Language.factory("language_detector", func=get_lang_detector)
    nlp.add_pipe("language_detector", last=True)
    doc = nlp(text)
    return doc._.language["language"]


# Wrapper functions for pandas methods


def show_analysis(analyzed_comments: list, n: int = 4) -> pd.DataFrame:

    """This function prints the head of the dataframe. The parameter n determines how many rows are printed
    It also returns the entire dataframe but does not print it"""

    print(f"Analysis of comments")
    df = pd.DataFrame(analyzed_comments)
    df.style.set_properties(**{"text-align": "center"})
    print(df.head(n))
    return df


def save_analysis(df: pd.DataFrame, filename: str) -> None or str:
    """To save the results to a CSV file, a filename must be provided.
    If a filename is not provided the function will not save file.
    """
    if filename:
        df.to_csv(f"analysis_{filename}.csv")
        print(f"saved to <analysis_{filename}.csv>")
        print("\n")
    else:
        return "A filename is required to save the results"
