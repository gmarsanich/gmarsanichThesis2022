import requests
import json


def get_comments(video_id: str):
    payload = {
        "key": "AIzaSyAPMn3uOPZrooP9pa4nSkQ7OZjIR-4MtJM",
        "textFormat": "plainText",
        "part": "snippet",
        "videoId": "",
        "maxResults": 100,
        "nextPageToken": "",
    }

    payload["videoId"] = video_id

    # https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyAPMn3uOPZrooP9pa4nSkQ7OZjIR-4MtJM&textFormat=plainText&part=snippet&videoId=EOxarwd3eTs&maxResults=9999

    comment_request = requests.get(
        "https://www.googleapis.com/youtube/v3/commentThreads?", params=payload
    )

    with open(f"comments_{str(video_id)}_raw.json", "wb") as fd:
        for chunk in comment_request.iter_content(chunk_size=128):
            fd.write(chunk)

    with open(f"comments_{video_id}_raw.json", "r", encoding="utf8") as f:
        data = json.load(f)

    # next_page_token = ""
    # next_page_token += data.get("nextPageToken")

    # while comment_request.status_code == 200:
    #       payload["nextPageToken"] = next_page_token
    #       print(next_page_token)

    # payload["nextPageToken"] = next_page_token
    # print(payload)

    # comment_request = requests.get(
    #     "https://www.googleapis.com/youtube/v3/commentThreads?", params=payload
    # )

    return data


def get_likes(video_id: str):

    payload = {"videoId": ""}
    payload["videoId"] = video_id

    likes = requests.get("https://returnyoutubedislikeapi.com/votes?", params=payload)

    with open(f"comments_{str(video_id)}_likes.json", "wb") as fd:
        for chunk in likes.iter_content(chunk_size=128):
            fd.write(chunk)

    return likes
