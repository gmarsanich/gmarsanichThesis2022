import time
import pandas as pd

import utils
from get_video import get_comments, get_id, get_likes, load_comments
from transformers.utils import logging


def main():
    # comments = get_comments("https://www.youtube.com/watch?v=4DCbZJh-Gk4")
    comments = load_comments("comments_4DCbZJh-Gk4.json")
    # video_id = get_id(url)

    ### Analysis

    checkpoints = {
        int(len(comments) * perc): perc * 100 for perc in [0.25, 0.5, 0.75, 0.9, 1]
    }

    start_time = time.time()

    df_list = []

    for i, comment in enumerate(comments):
        current_time = time.time()
        elapsed_time = current_time - start_time

        lang = utils.detect_language(comment)

        # Vader
        vader_score = utils.vader_classifier(comment)

        # TextBlob - Polarity is a a float between -1 and 1 where -1 is negative and 1 is positive
        blob_score = utils.textblob_classifier(comment)

        # Bert
        bert_score = utils.bert_classifier(comment)

        df_dict = {
            "Comment": comment,
            "Language": lang,
            "Vader score": vader_score,
            "Textblob score": blob_score,
            "BERT score": bert_score,
        }

        df_list.append(df_dict)

        if i + 1 in checkpoints:
            print(
                f"{checkpoints[i+1] :.0f}% of the comments have been analyzed\nTime elapsed: {elapsed_time :.2f} seconds"
            )  # shamelessly stolen from Comp. Ling. Notebook 8

    df = pd.DataFrame(df_list)
    utils.save_analysis(df, "test_debug")

    # print(get_likes(url))  # only prints likes and dislikes
    # print(get_likes(url, v=True))  # prints all data related to the video


if __name__ == "__main__":
    logging.set_verbosity_error()
    main()
