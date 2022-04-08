import os
import logging
from get_video import get_comments, get_likes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification
import pandas as pd
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

# Suppressing warnings
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


# Some useful functions we will use later


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


def show_analysis(model_name: str, analyzed_comments: list) -> None:

    """This function prints the analysis of the given list of comments"""

    print(f"{model_name} analysis")
    df = pd.DataFrame(analyzed_comments)
    df.style.set_properties(**{"text-align": "center"})
    print(df.head())
    mean = df["Score"].mean()
    print("Mean sentiment score: ", mean)
    print("\n")


url = str(input("Enter a YouTube URL: "))

comments = get_comments(url)

### Analysis
vader_list = []
blob_list = []
bert_list = []

# Bert analyzer
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Vader analyzer
analyzer = SentimentIntensityAnalyzer()
"""positive sentiment: compound score >= 0.05
    neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
    negative sentiment: compound score <= -0.05
NOTE: The compound score is the one most commonly used for sentiment analysis by most researchers, including the authors."""

for comment in comments:

    lang = detect_language(comment)

    # Vader
    vs = analyzer.polarity_scores(comment)
    vader_dict = {
        "Comments": comment,
        "Score": vs["compound"],
        "Language": lang,
    }
    vader_list.append(vader_dict)

    # TextBlob
    blob = TextBlob(comment)
    textblob_dict = {
        "Comments": comment,
        "Score": blob.sentiment.polarity,
        "Language": lang,
    }  # Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
    blob_list.append(textblob_dict)

    # Bert
    c = classifier(comment)
    bert_dict = {
        "Comments": comment,
        "Score": c[0]["score"],
        "Language": lang,
    }
    bert_list.append(bert_dict)

show_analysis("Vader", vader_list)
show_analysis("Texblob", blob_list)
show_analysis("BERT", bert_list)

likes = print(get_likes(url))
likes_verbose = print(get_likes(url, True))
