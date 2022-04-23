from itertools import combinations

import pandas as pd
import spacy
from scipy.stats import pearsonr
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from textblob import TextBlob
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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


def bert_classifier(s: str) -> float:

    """This function returns a sentiment score using the BERT sentiment analysis pipeline"""

    model_name = "distilbert-base-multilingual-cased"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    classifier = pipeline(
        "sentiment-analysis", model=model, tokenizer=tokenizer, device=0
    )

    initial_str = classifier(s)

    label, score = initial_str[0]["label"], initial_str[0]["score"]

    pos = ["5 stars", "4 stars"]
    neg = ["1 star", "2 stars"]
    neutral = ["2 stars", "3 stars"]

    if label in pos or label in neutral:
        return score
    if label in neg:
        return score * -1


def vader_classifier(s: str) -> float:

    """This function returns a sentiment score using the Vader sentiment analysis pipeline"""

    # positive sentiment: compound score >= 0.05
    # neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
    # negative sentiment: compound score <= -0.05
    # NOTE: The compound score is the one most commonly used for sentiment analysis by most researchers, including the authors.

    analyzer = SentimentIntensityAnalyzer()

    vs = analyzer.polarity_scores(s)
    vader_score = vs["compound"]
    return vader_score


def textblob_classifier(s: str) -> float:

    """This function returns a sentiment score using the TextBlob classifier"""

    blob = TextBlob(s)
    blob_score = blob.sentiment.polarity
    return blob_score


# Wrapper functions for pandas methods


def show_analysis(analyzed_comments: list, n: int = 4) -> pd.DataFrame:

    """This function prints the head of the dataframe. The parameter n determines how many rows are printed
    It also returns the entire dataframe but does not print it
    """

    print(f"Analysis of comments")
    df = pd.DataFrame(analyzed_comments)
    df.style.set_properties(**{"text-align": "center"})
    print(df.head(n))
    return df


def save_analysis(df: pd.DataFrame, filename: str) -> None or str:
    """To save the results to a CSV file, a filename must be provided.
    If a filename is not provided the function will not save to file.
    """
    if filename:
        df.to_csv(f"analysis_{filename}.csv")
        print(f"saved to <analysis_{filename}.csv>")
    else:
        return "A filename is required to save the results"
