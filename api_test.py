import json
from get_video import get_comments, get_likes

# https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyAPMn3uOPZrooP9pa4nSkQ7OZjIR-4MtJM&textFormat=plainText&part=snippet&videoId=EOxarwd3eTs&maxResults=9999
# https://returnyoutubedislikeapi.com/votes?videoId=EOxarwd3eTs

data = get_comments("EOxarwd3eTs")

comments = []
data_comments = data["items"]

for idx, comment in enumerate(data_comments):
    comment = data_comments[idx]
    comments.append(
        (
            comment.get("snippet")
            .get("topLevelComment")
            .get("snippet")
            .get("textOriginal")
        )
    )

comments_to_file = [comment.strip() for comment in comments]

with open(f"comments.json", "w", encoding="utf8") as f:
    json.dump(
        comments_to_file,
        f,
    )
