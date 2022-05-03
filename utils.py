import os
import pathlib
import shutil

import langdetect as ld
import pandas as pd
import spacy
from googletrans import Translator, constants
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from textblob import TextBlob
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import httpx


def detect_language(text: str) -> str:

    """This function detects the language of a given text"""

    try:
        lang = ld.detect(text)
    except ld.lang_detect_exception.LangDetectException:
        lang = "NA"
    return lang


def translate(text: str) -> str:

    """This function translates a given text into English using the Googletrans library"""
    timeout = httpx.Timeout(3)
    translator = Translator(timeout=timeout)
    try:
        result = translator.translate(text)
    except ValueError:
        result = text
    return result.text


def bert_classifier(lst: list) -> list:

    """This function returns a sentiment score using the BERT sentiment analysis pipeline
    This function is fundamentally different from the other 2 analysis functions in this file:
    If a single input is passed, the BERT based classifier can take around 15 seconds to process it and return a score
    Instead, if a list of inputs is passed, the classifier is likely to take up less time.
    For example, iterating through a list of n strings and passing each element through the classifier,
    we can expect a computation time of ~15 * n seconds. If an entire list is passed, this is not the case.
    For 100 strings, we can expect this classifier to take around 30-40 seconds to process the entire list.
    This is still orders of magnitude slower than Vader or Textblob, but it means that it can process 100 strings in less than 20 minutes
    """

    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    classifier = pipeline(
        "sentiment-analysis", model=model, tokenizer=tokenizer, device=0
    )

    t = classifier(lst, truncation=True)  # classifier returns list of dict

    l = []

    pos = ["5 stars", "4 stars"]
    neg = ["1 star", "2 stars"]
    neutral = ["2 stars", "3 stars"]

    for dict_, comment in zip(t, lst):

        if dict_["label"] in pos or dict_["label"] in neutral:
            dict_["score"] *= 1

        if dict_["label"] in neg:
            dict_["score"] *= -1

        l.append(dict_["score"])

    return l


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


def generate_labels(lst: list, model_name: str) -> list:

    """This function generates labels for sentiment scores for a given model"""

    if model_name == "vader":
        vader_labels = []
        for score in lst:
            if score >= 0.05:
                vader_labels.append("Positive")
            if score > -0.05 and score < 0.05:
                vader_labels.append("Neutral")
            if score <= -0.05:
                vader_labels.append("Negative")
        return vader_labels

    if model_name == "bert":
        bert_labels = []
        for score in lst:
            if score >= 0.33:
                bert_labels.append("Positive")
            if score >= 0 and score < 0.33:
                bert_labels.append("Netural")
            if score < 0:
                bert_labels.append("Negative")
        return bert_labels

    if model_name == "blob":
        blob_labels = []
        for score in lst:
            if score >= 0.33:
                blob_labels.append("Positive")
            if score >= 0 and score < 0.33:
                blob_labels.append("Netural")
            if score < 0:
                blob_labels.append("Negative")
        return blob_labels


def save_analysis(df: pd.DataFrame, filename: str) -> None or str:
    """To save the results to a CSV file, a filename must be provided.
    If a filename is not provided the function will not save to file.
    """
    if filename:
        df.to_csv(f"analysis_{filename}.csv", index=False)
        print(f"saved to <analysis_{filename}.csv>")
    else:
        return "A filename is required to save the results"


def move_dir(
    filename: str, destination: str, pattern: str = "*", source: str = os.getcwd()
) -> None:
    """This function moves a file to a new directory"""
    curdir = source
    original = f"{curdir}\\{filename}"
    target = f"{destination}\\{filename}"
    shutil.move(original, target)
    print(f"Moved <{filename}> to <{target}>")
