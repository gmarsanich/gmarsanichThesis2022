import requests
import json
import googleapiclient.discovery
import key

# Code adapted from https://developers.google.com/youtube/v3/docs/commentThreads/
def get_comments(video_id: str):

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = key.API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    request = youtube.commentThreads().list(
        part="snippet", maxResults=100, textFormat="plainText", videoId=video_id
    )
    response = request.execute()

    print(response["nextPageToken"])

    comments = []
    data_comments = response["items"]

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

    with open(f"comments_{video_id}.json", "a", encoding="utf8") as comments_file:
        json.dump(comments, comments_file)

    print(f"Written {len(comments)} comments to {comments_file.name}")
    return comments


def get_likes(video_id: str):

    payload = {"videoId": ""}
    payload["videoId"] = video_id

    likes = requests.get("https://returnyoutubedislikeapi.com/votes?", params=payload)

    with open(f"comments_{str(video_id)}_likes.json", "wb") as fd:
        for chunk in likes.iter_content(chunk_size=128):
            fd.write(chunk)

    return likes
