import requests
import json
import googleapiclient.discovery
import key__
from os import path
from pytube import extract


def get_id(video_url: str) -> str:

    """Takes a YouTube video url and extracts the ID by using the extract function from the pytube package and returns it"""

    id_ = extract.video_id(video_url)
    return id_


def get_title(video_url: str) -> str:

    """Takes a YouTube video url and extracts the title by using the title method from the pytube package and returns it"""

    return video_url.title


def call_yt_api(video_id: str) -> list:

    """This function is not intended for use in the main application.
    It calls the YouTube API and collects the json response with raw comment data.
    It then removes any data that is not the comment text and writes it to a json file
    Code adapted from https://developers.google.com/youtube/v3/docs/commentThreads/"""

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = key__.API_KEY  # Your YouTube API key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    request = youtube.commentThreads().list(
        part="snippet", maxResults=100, textFormat="plainText", videoId=video_id
    )
    response = request.execute()

    # print(response["nextPageToken"])

    comments = []
    data_comments = response["items"]

    for comment in data_comments:
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


def get_comments(video_url: str) -> list:

    """This function searches the current working directory for a file matching the filename parameter
    If a matching file is found, its contents will be anaylzed so that unnecessary API calls are not made.
    If the file is not found, it calls the call_yt_api function defined earlier

    """

    video_id = get_id(video_url)
    filename = f"comments_{video_id}.json"
    if path.exists(filename):
        with open(filename, "r") as f:
            comments = json.load(f)
            print(f"Reading from local file <{filename}>")
            return comments
    else:
        return call_yt_api(video_id)


def get_likes(video_url: str, v=False) -> str:

    """Calls the Return YouTube Dislike API and saves the json response

    It takes an optional argument v. If v is true, then the function returns all the data associated with the video
    Otherwise, it only returns the likes and dislikes

    Code adapted from returnyoutubedislike.com

    """

    video_id = get_id(video_url)

    payload = {"videoId": video_id}

    data = requests.get("https://returnyoutubedislikeapi.com/votes?", params=payload)

    with open(f"comments_{str(video_id)}_likes.json", "wb") as fd:
        for chunk in data.iter_content(chunk_size=128):
            fd.write(chunk)

    with open(f"comments_{str(video_id)}_likes.json", "r") as f:
        data = json.load(f)

    ratio = round(data["likes"] / data["dislikes"], 3)

    if v:
        return f"The video with ID <{video_id}> has the following data: {data}"
    else:
        return f"The video with ID <{video_id}> has the following like to dislike counts: {data['likes']} - {data['dislikes']}\nRatio = {ratio}"
