from get_video import get_comments, get_likes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer as nba
from transformers import pipeline
import pandas as pd

comments = get_comments("https://www.youtube.com/watch?v=JZBLN-42BY0")
likes = print(get_likes("https://www.youtube.com/watch?v=JZBLN-42BY0"))

# Vader
print("Vader analysis")
vader_list = []
analyzer = SentimentIntensityAnalyzer()
for comment in comments:
    vs = analyzer.polarity_scores(comment)
    vader_dict = {"Comments": comment, "Score": vs}
    vader_list.append(vader_dict)
vader_df = pd.DataFrame(vader_list)
print(vader_df.head())

# TextBlob
print("TextBlob analysis")
textblob_list = []
for comment in comments:
    blob = TextBlob(comment)
    blob.sentiment.polarity
    textblob_dict = {
        "Comments": comment,
        "Score": blob.sentiment.polarity,
    }  # Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
    textblob_list.append(textblob_dict)
textblob_df = pd.DataFrame(textblob_list)
print(textblob_df.head())

# Hugging Face (BERT)
print("BERT analysis")
bert_list = []
classifier = pipeline("sentiment-analysis")
for comment in comments:
    classifier(comment)
    bert_dict = {
        "Comments": comment,
        "Score": classifier(comment),
    }  # the label and score are separated - negative with high score means highly negative and vice versa
    bert_list.append(bert_dict)
bert_df = pd.DataFrame(bert_list)
print(bert_df.head())
