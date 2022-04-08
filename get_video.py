import requests
import json
import googleapiclient.discovery
import key
from pytube import extract


def get_id(video_url: str) -> str:

    """Takes a YouTube video url and extracts the ID by using the extract function from the pytube package and returns it"""

    id_ = extract.video_id(video_url)
    return id_


def get_comments(video_url: str) -> list:

    """Calls the YouTube API and collects the json response with raw comment data. It then removes any data that is not the comment text and writes it to a json file
    Code adapted from https://developers.google.com/youtube/v3/docs/commentThreads/

    """

    video_id = get_id(video_url)

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

    #print(response["nextPageToken"])

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


def get_likes(video_url: str, v=False) -> str:

    """Calls the Return YouTube Dislike API and saves the json response
    param video_url: str
    param v: bool

    It takes an optional argument v. If v is true, then the function returns all the data associated with the video
    Otherwise, it only returns the likes and dislikes

    Code adapted from returnyoutubedislike.com

    """

    video_id = get_id(video_url)

    payload = {"videoId": ""}
    payload["videoId"] = video_id

    likes = requests.get("https://returnyoutubedislikeapi.com/votes?", params=payload)

    with open(f"comments_{str(video_id)}_likes.json", "wb") as fd:
        for chunk in likes.iter_content(chunk_size=128):
            fd.write(chunk)

    with open(f"comments_{str(video_id)}_likes.json", "r") as f:
        likes = json.load(f)

    if v:
        return f"The video with ID {video_id} has the following data: {likes}"
    else:
        return f"The video with ID {video_id} has the following like to dislike ratio: {likes['likes']} - {likes['dislikes']}"
