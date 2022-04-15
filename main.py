import os
import logging
from get_video import get_comments, get_likes, get_id
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification
import pandas as pd
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

# Suppressing warnings and setting up TensorFlow GPU
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


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


def show_analysis(
    model_name: str, analyzed_comments: list, save: bool = False, filename: str = None
) -> None:

    """This function prints the analysis of the given list of comments
    The function has 2 optional parameters: save and filename. To save the results to a CSV file, save must be True and a filename must be provided.
    If a filename is not provided and save is True, the function will throw an assertion error.
    If a filename is provided and save is False, the function will not save the results to file.
    """

    print(f"{model_name} analysis")
    df = pd.DataFrame(analyzed_comments)
    df.style.set_properties(**{"text-align": "center"})
    print(df.head())
    mean = df["Sentiment score"].mean()
    print("Mean sentiment score: ", mean)
    if save:
        assert filename is not None, "You must provide a title for the filename"
        df.to_csv(f"analysis_{filename}.csv")
        print(f"saved to <analysis_{filename}.csv>")
        print("\n")
    return df


def main():
    url = str(input("Enter a YouTube URL: "))
    comments = get_comments(url)
    video_id = get_id(url)

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
            "Sentiment score": vs["compound"],
            "Language": lang,
        }
        vader_list.append(vader_dict)

        # TextBlob
        blob = TextBlob(comment)
        textblob_dict = {
            "Comments": comment,
            "Sentiment score": blob.sentiment.polarity,
            "Language": lang,
        }  # Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
        blob_list.append(textblob_dict)

        # Bert
        c = classifier(comment)
        bert_dict = {
            "Comments": comment,
            "Sentiment score": c[0]["score"],
            "Language": lang,
        }
        bert_list.append(bert_dict)

    show_analysis("Vader", vader_list, save=True, filename=f"{video_id}_vader")
    show_analysis("Texblob", blob_list, save=True, filename=f"{video_id}_blob")
    show_analysis("BERT", bert_list, save=True, filename=f"{video_id}_bert")

    print(get_likes(url))  # only prints likes and dislikes
    print(get_likes(url, v=True))  # prints all data related to the video


if __name__ == "__main__":
    main()
