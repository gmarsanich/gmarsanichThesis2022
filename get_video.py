import json
from os import path

import googleapiclient.discovery
import requests
from pytube import extract

import key__


def get_id(video_url: str) -> str:

    """Takes a YouTube video url and extracts the ID by using the extract function from the pytube package and returns it"""

    id_ = extract.video_id(video_url)
    return id_


def get_comments(video_url: str) -> list:

    """This function is not intended for use in the main application.
    It calls the YouTube API and collects the json response with raw comment data.
    It then removes any data that is not the comment text and writes it to a json file
    Code adapted from https://developers.google.com/youtube/v3/docs/commentThreads/"""

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = key__.API_KEY  # Your YouTube API key
    comments = []

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    def save_comments(response: dict) -> None:
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            comments.append(
                text.strip()
            )  # creating the list list of comments within the function, appending to it and returning it breaks the loop and it will always return 100 comments

    def get_comment_threads(youtube: object, video_id: str, nextPageToken: str):
        results = (
            youtube.commentThreads()
            .list(
                part="snippet",
                maxResults=100,
                videoId=video_id,
                textFormat="plainText",
                pageToken=nextPageToken,
            )
            .execute()
        )
        return results

    video_id = get_id(video_url)
    response = get_comment_threads(youtube, video_id, "")
    next_page_token = response["nextPageToken"]
    save_comments(response)

    try:
        while next_page_token:
            response = get_comment_threads(youtube, video_id, next_page_token)
            next_page_token = response["nextPageToken"]
            save_comments(response)
    except KeyError:
        with open(f"comments_{video_id}.json", "a", encoding="utf-8") as comments_file:
            json.dump(comments, comments_file, ensure_ascii=False)

    print(f"Written {len(comments)} comments to {comments_file.name}")

    return comments


def load_comments(filename: str) -> list:

    """This function searches the current working directory for a file matching the filename parameter
    If a matching file is found, it will be loaded and its contents will be returned.

    """

    if path.exists(filename):
        print(f"Reading from local file <{filename}>")
        with open(filename, "r", encoding="utf-8") as f:
            comments = json.load(f)
            return comments
    else:
        assert False, f"File <{filename}> not found"


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
        return f"The video with ID <{video_id}> has the following like to dislike counts: {data['likes']} - {data['dislikes']}\nRatio = {ratio} likes for every dislike"
