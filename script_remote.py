import json
import requests
import os
import praw
import config
from datetime import datetime
from datetime import timedelta

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0"}

LOG_FILE = "./shortcodes.txt"

IGS_FILE = "./ig_usernames.txt"

URL = "https://www.instagram.com/"


def load_file(file: str):
    """Loads the log file and creates it if it doesn't exist.
     Parameters
    ----------
    file : str
        The file to write down
    Returns
    -------
    list
        A list of urls.
    """

    try:
        with open(file, 'r', encoding='utf-8') as temp_file:
            return temp_file.read().splitlines()
    except Exception:

        with open(LOG_FILE, 'w', encoding='utf-8') as temp_file:
            return []


def update_file(file_name: str, data: str):
    """Updates the log file_name.
    Parameters
    ----------
    file_name : str
        The file_name to write down.
    data : str
        The data to log.
    """

    with open(file_name, 'a', encoding='utf-8') as temp_file:
        temp_file.write(data + '\n')


def get_ig_posts(ig_pages: list):
    """Get the json from IG webpage then converts it into a list of dict.
    Parameters
    ----------
    ig_pages : list
        list of strings.
    """
    post_list = list()

    for page in ig_pages:

        url = URL + page

        response = requests.get(url, headers=HEADERS)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(str(e))
            continue

        data = response.text

        start = data.index('_sharedData')

        end = data.index(';</script>')

        json_data = data[start+14:end]

        try:
            json_data = json.loads(json_data)['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        except Exception as e:
            print(str(e))
            continue

        tolerance_time = datetime.today() - timedelta(hours=6)

        for item in json_data[:4]:

            # Put validations here
            post_datetime = datetime.fromtimestamp(item['node']['taken_at_timestamp'])

            if post_datetime >= tolerance_time:

                text = item['node']['edge_media_to_caption']["edges"][0]["node"]["text"].replace("\n", "").replace("@", "").split('.')[0]

                post_list.append({
                    'display_url': item['node']['display_url'],
                    'shortcode': item['node']['shortcode'],
                    'text': text,
                    'likes': item['node']['edge_liked_by']['count']
                })

        print(f'--------\nGot images posts from : {url}')

    return post_list

def get_image(url: str):
    """Get the from url.
    Parameters
    ----------
    url : srt
        img url.
    """
    image_path = './temp.jpg'

    with open(image_path,'wb') as temp_file:

            imagen = requests.get(url,headers=HEADERS).content

            temp_file.write(imagen)

    return image_path


def post_on_reddit(posts: list):
    """Post the a list of dict on reddit.
    Parameters
    ----------
    posts : list
        the list of IG posts dict.
    """

    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    _log = load_file(LOG_FILE)

    for idx, post in enumerate(posts, start=1):

        #if post['shortcode'] in _log:
        #    continue

        _img = get_image(post['display_url'])

        #reddit.subreddit(config.SUBREDDIT).submit(title=post['text'], url=URL+"p/"+post['shortcode'])
        submission = reddit.subreddit(config.SUBREDDIT).submit_image(post['text'], _img)

        submission.reply("Fuente: {}".format(URL+"p/"+post['shortcode']))
        print(f'---------\nPosting image: {idx}')

        #update_file(LOG_FILE, post['shortcode'])

        os.remove(_img)


if __name__ == "__main__":

    ig_usernames = load_file(IGS_FILE)

    _posts = get_ig_posts(ig_usernames)

    print(f'------\nPosts counts: {len(_posts)}')

    if len(_posts) < 1:
        print(f'------ There\'s no new posts; End of script\n:')

    post_on_reddit(_posts)
