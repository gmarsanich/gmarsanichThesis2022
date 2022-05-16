import json
from os import path

import googleapiclient.discovery
import requests
from pytube import extract
from serpapi import GoogleSearch

import key__


def get_videos(search_term: str) -> list:

    """This function takes a search term and returns a list of videos related to that term
    BEWARE: this function returns a list of lists which I can't seem to be able to flatten within the function
    """

    params = {
        "api_key": key__.SEARCH_KEY,
        "engine": "youtube",
        "search_query": search_term,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    response = []
    for result in results["video_results"]:
        response.append(result["link"])

    return response


def get_id(video_url: str) -> str:

    """Takes a YouTube video url and extracts the ID by using the extract function from the pytube package and returns it"""

    id_ = extract.video_id(video_url)
    return id_


def get_comments(video_url: str) -> list:

    """This collects YouTube comments using the YouTube API
    It calls the YouTube API and collects the json response with raw comment data.
    It then removes any data that is not the comment text and writes it to a json file
    It's also a mess
    Code adapted from https://developers.google.com/youtube/v3/docs/commentThreads/"""

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = key__.API_KEY  # Your YouTube API key
    comments = []

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    def extract_comments(response: dict) -> None:
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            clean = text.strip()
            comments.append(clean)
            # creating the list list of comments within the function, appending to it and returning it breaks the loop and it will always return 100 comments

    # special case for videos with less than 100 commments
    def get_comment_threads_no_npt(youtube: object, video_id: str) -> dict:
        results = (
            youtube.commentThreads()
            .list(
                part="snippet",
                maxResults=100,
                videoId=video_id,
                textFormat="plainText",
            )
            .execute()
        )
        return results

    def get_comment_threads(youtube: object, video_id: str, nextPageToken: str) -> dict:
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

    def save_comments(filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as comments_file:
            json.dump(comments, comments_file, ensure_ascii=False)
        print(f"Written <{len(comments)}> comments to <{comments_file.name}>")

    video_id = get_id(video_url)
    response = get_comment_threads(youtube, video_id, "")

    # If a video has less than 100 comments, run the no_npt version of the function

    try:
        next_page_token = response["nextPageToken"]
    except KeyError:
        response = get_comment_threads_no_npt(
            youtube,
            video_id,
        )
        extract_comments(response)
        save_comments(filename=f"comments_{video_id}.json")
        return comments

    # If it has more than 100 comments, keep trying until next_page_token is empty

    try:
        while next_page_token and len(comments) <= 500:
            response = get_comment_threads(youtube, video_id, next_page_token)
            next_page_token = response["nextPageToken"]
            extract_comments(response)
    except KeyError:
        save_comments(filename=f"comments_{video_id}.json")

    save_comments(filename=f"comments_{video_id}.json")

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


def get_likes(video_url: str) -> str or dict:

    """Calls the Return YouTube Dislike API and saves the json response
    Code adapted from returnyoutubedislike.com

    """

    video_id = get_id(video_url)

    payload = {"videoId": video_id}

    data = requests.get("https://returnyoutubedislikeapi.com/votes?", params=payload)

    data = data.json()

    likes, dislikes = data["likes"], data["dislikes"]

    return {"URL": video_url, "likes": likes, "dislikes": dislikes}
