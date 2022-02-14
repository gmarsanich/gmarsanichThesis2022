import requests
import json


def get_comments(video_id: str):
    payload = {
        "key": "AIzaSyAPMn3uOPZrooP9pa4nSkQ7OZjIR-4MtJM",
        "textFormat": "plainText",
        "part": "snippet",
        "videoId": "",
        "maxResults": 100,
    }

    payload["videoId"] = video_id

    # print(payload)

    # https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyAPMn3uOPZrooP9pa4nSkQ7OZjIR-4MtJM&textFormat=plainText&part=snippet&videoId=EOxarwd3eTs&maxResults=9999

    comment_request = requests.get(
        "https://www.googleapis.com/youtube/v3/commentThreads?", params=payload
    )

    # print(r.json())

    with open(f"comments_{str(video_id)}_raw.json", "wb") as fd:
        for chunk in comment_request.iter_content(chunk_size=128):
            fd.write(chunk)

    with open(f"comments_{video_id}_raw.json", "r", encoding="utf8") as f:
        data = json.load(f)

    return data


def get_likes(*video_id: str):
    assert False, "Not implemented"


get_comments("EOxarwd3eTs")
