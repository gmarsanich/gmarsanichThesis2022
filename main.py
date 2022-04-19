import logging
import os
import time

import pandas as pd
from textblob import TextBlob
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from get_video import get_comments, get_id, get_likes, load_comments
import utils

# Suppressing warnings and setting up TensorFlow GPU
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def main():
    # url = str(input("Enter a YouTube URL: "))
    # comments = get_comments(url)
    comments = load_comments("")
    # video_id = get_id(url)

    ### Analysis
    df_list = []

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

    checkpoints = {
        int(len(comments) * perc): perc * 100 for perc in [0.25, 0.5, 0.75, 0.9, 1]
    }

    start_time = time.time()

    for i, comment in enumerate(comments):
        current_time = time.time()
        elapsed_time = current_time - start_time

        lang = utils.detect_language(comment)

        # Vader
        vs = analyzer.polarity_scores(comment)
        vader_score = vs["compound"]

        # TextBlob - Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
        blob = TextBlob(comment)
        blob_score = blob.sentiment.polarity

        # Bert
        c = classifier(comment)
        bert_score = c[0]["score"]

        df_dict = {
            "Comment": comment,
            "Vader score": vader_score,
            "Textblob score": blob_score,
            "BERT score": bert_score,
            "Language": lang,
        }

        df_list.append(df_dict)

        if i + 1 in checkpoints:
            print(
                f"{checkpoints[i+1] :.0f}% of the comments have been analyzed\nTime elapsed: {elapsed_time :.2f} seconds"
            )  # shamelessly stolen from Comp. Ling. Notebook 8

    df = utils.show_analysis(df_list, 10)
    print(len(comments))
    utils.save_analysis(df, "test")

    # print(get_likes(url))  # only prints likes and dislikes
    # print(get_likes(url, v=True))  # prints all data related to the video


if __name__ == "__main__":
    main()
