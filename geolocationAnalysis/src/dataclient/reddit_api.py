# Write a code in python using reddit api to get all posts and comments from a subreddit

import praw
import config

reddit = praw.Reddit(
    client_id=config.client_id,
    client_secret=config.client_secret,
    user_agent=config.user_agent,
)
# username=config.username,
# password=config.password)

subreddit = reddit.subreddit("python")

hot_python = subreddit.hot(limit=5)

for submission in hot_python:
    if not submission.stickied:
        print(f"Title: {submission.title} \nText: {submission.selftext}")
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.body != "[deleted]":
                print(comment.body)
        print()
