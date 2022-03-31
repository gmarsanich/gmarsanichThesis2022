from get_video import get_comments, get_likes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification
import pandas as pd

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

for comment in comments:
    # Vader
    vs = analyzer.polarity_scores(comment)
    vader_dict = {"Comments": comment, "Score": vs["compound"]}
    vader_list.append(vader_dict)

    # TextBlob
    blob = TextBlob(comment)
    textblob_dict = {
        "Comments": comment,
        "Score": blob.sentiment.polarity,
    }  # Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
    blob_list.append(textblob_dict)

    # Bert
    c = classifier(comment)
    bert_dict = {"Comments": comment, "Score": c[0]["score"]}
    bert_list.append(bert_dict)

print("Vader analysis")
vader_df = pd.DataFrame(vader_list)
print(vader_df.head())
vader_mean = vader_df["Score"].mean()
print("Mean sentiment score: ", vader_mean)
print("\n")

print("TextBlob analysis")
textblob_df = pd.DataFrame(blob_list)
print(textblob_df.head())
textblob_mean = textblob_df["Score"].mean()
print("Mean sentiment score: ", textblob_mean)
print("\n")

print("BERT analysis")
bert_df = pd.DataFrame(bert_list)
print(bert_df.head())
bert_mean = bert_df["Score"].mean()
print("Mean sentiment score: ", bert_mean)
print("\n")

likes = print(get_likes(url))
likes_verbose = print(get_likes(url, True))
