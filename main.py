from get_video import get_comments, get_likes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer as nba
from transformers import pipeline
import pandas as pd

url = "https://www.youtube.com/watch?v=JZBLN-42BY0"

comments = get_comments(url)

# Analysis
vader_list = []
blob_list = []
bert_list = []
classifier = pipeline("sentiment-analysis")
analyzer = SentimentIntensityAnalyzer()

for comment in comments:
    # Vader
    vs = analyzer.polarity_scores(comment)
    vader_dict = {"Comments": comment, "Score": vs["compound"]}
    vader_list.append(vader_dict)

    # TextBlob
    blob = TextBlob(comment)
    blob.sentiment.polarity
    textblob_dict = {
        "Comments": comment,
        "Score": blob.sentiment.polarity,
    }  # Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
    blob_list.append(textblob_dict)

    # Bert
    # the label and score are separated - negative with high score means highly negative and vice versa.
    # I apply a simple function to keep the scoring system consistent
    c = classifier(comment)
    label = c[0]["label"]
    score = c[0]["score"]
    if label == "NEGATIVE":
        score *= -1
    bert_dict = {
        "Comments": comment,
        "Score": score,
    }
    bert_list.append(bert_dict)

print("Vader analysis", end="")
vader_df = pd.DataFrame(vader_list)
print(vader_df.head())
vader_mean = vader_df["Score"].mean()
print("Mean sentiment score: ", vader_mean, end="\n")

print("TextBlob analysis", end="")
textblob_df = pd.DataFrame(blob_list)
print(textblob_df.head())
textblob_mean = textblob_df["Score"].mean()
print("Mean sentiment score: ", textblob_mean, end="\n")

print("BERT analysis", end="")
bert_df = pd.DataFrame(bert_list)
print(bert_df.head())
bert_mean = bert_df["Score"].mean()
print("Mean sentiment score: ", bert_mean, end="\n")

likes = print(get_likes(url))
likes_verbose = print(get_likes(url, True))