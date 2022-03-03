from get_video import get_comments, get_likes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

comments = get_comments("https://www.youtube.com/watch?v=JZBLN-42BY0")
likes = print(get_likes("https://www.youtube.com/watch?v=JZBLN-42BY0"))

analyzer = SentimentIntensityAnalyzer()

for sentence in comments:
    vs = analyzer.polarity_scores(sentence)
    print(f'{sentence:-<65} {vs}')