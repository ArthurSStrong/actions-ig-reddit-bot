import os

APP_ID = (os.environ['APP_ID'] if 'APP_ID'
             in os.environ else '')
APP_SECRET = (os.environ['APP_SECRET'] if 'APP_SECRET'
             in os.environ else '')
REDDIT_USERNAME = (os.environ['REDDIT_USERNAME'] if 'REDDIT_USERNAME'
             in os.environ else '')
REDDIT_PASSWORD = (os.environ['REDDIT_PASSWORD'] if 'REDDIT_PASSWORD'
             in os.environ else '')
USER_AGENT = "linux:larry3000bot_script:v0.0.1 (by /u/larry3000bot)"
SUBREDDIT = "larry3000bot"
