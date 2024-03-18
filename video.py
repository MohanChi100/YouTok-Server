from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime
import datetime
import random
from langdetect import detect
import emoji
# from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

API_KEY = 'AIzaSyCfSdnud7WLOsz-cdUh2FgPwDsCQSGjHpk' #shorts
# API_KEY = 'AIzaSyDD56062udoEeGQ5pRkEfxKXQ7IPCRYMEs'

MAX_RESULT = 50
MAX_COMMENT_RESULT = 10
# Next_PAGE_TOKEN = None
THUMBNAIL_FOLDER= 'static/YouTube_shorts_thumbnail/'

def youtube_search(query, PAGE_TOKEN, max_results=MAX_RESULT):
    print('query: ' + query)
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        # page token is none at the first time
        # global Next_PAGE_TOKEN
        # Call the search.list method to search for videos
        search_response = youtube.search().list(
            q=query + ' shorts',
            part='snippet',
            type='video',
            order='viewCount',
            # relevanceLanguage='en',
            # videoCategoryId=42, #shorts
            videoDuration='short',
            maxResults=max_results,
            pageToken=PAGE_TOKEN,
        ).execute()
        videos_list = []
        # print(search_response)
        for search_result in search_response.get('items', []):
            print(search_result)
            if search_result['id']['kind'] == 'youtube#video':
                video = {
                    'title': search_result['snippet']['title'],
                    'video_id': search_result['id']['videoId'],
                }
                videos_list.append(video)
        Next_PAGE_TOKEN = search_response.get('nextPageToken')
        
        return videos_list, Next_PAGE_TOKEN
    except HttpError as e:
        print('An HTTP error occurred:', e)
        return None

def youtube_search_publish_date(query, publishedAfter, publishedBefore, max_results=MAX_RESULT):
    # print('query: ' + query)
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        # page token is none at the first time
        global Next_PAGE_TOKEN
        # Call the search.list method to search for videos
        search_response = youtube.search().list(
            q=query + ' shorts',
            # q=query,
            part='snippet',
            type='video',
            order='viewCount',
            # relevanceLanguage='en',
            # videoCategoryId=42, #shorts
            videoDuration='short',
            publishedAfter=publishedAfter,
            publishedBefore=publishedBefore,
            maxResults=max_results,
            pageToken=Next_PAGE_TOKEN,
        ).execute()
        videos_list = []
        # print(search_response)
        for search_result in search_response.get('items', []):
            print(search_result)
            if search_result['id']['kind'] == 'youtube#video':
                # try:
                #     title = search_result['snippet']['title'].replace('#', ' ')
                #     print('remove #: ' + title)
                #     language = detect(title)
                # except:
                #     language = 'Unknown'
                video = {
                    'title': search_result['snippet']['title'],
                    'video_id': search_result['id']['videoId'],
                    # 'language': language
                }
                videos_list.append(video)
        Next_PAGE_TOKEN = search_response.get('nextPageToken')
        print('Next_PAGE_TOKENNext_PAGE_TOKENNext_PAGE_TOKEN:' + Next_PAGE_TOKEN)
        return videos_list
    except HttpError as e:
        print('An HTTP error occurred:', e)
        return None

def get_video_metadata(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        # Call the videos.list method to get the video details
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        if len(video_response['items']) == 0:
            print('Video not found.')
            return None
        video_result = video_response['items'][0]
        # print(video_result)
        # print(video_result['snippet']['categoryId'])
        
        return video_result

    except HttpError as e:
        print('An HTTP error occurred:', e)
        return None

def get_video_comments(video_id, max_comment_results = MAX_COMMENT_RESULT):
    max_comment_results = random.randint(10, 20)
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    comments = []
    nextPageToken = None

    while True:
        # Call the API to get comments
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=max_comment_results,
            pageToken=nextPageToken
        ).execute()

        for item in response['items']:
            comment_data = item['snippet']['topLevelComment']['snippet']

            comment = comment_data['textDisplay']
            like_count = comment_data['likeCount']
            profile_image_url = comment_data['authorProfileImageUrl']
            author_name = comment_data['authorDisplayName']
            publish_date = process_time(comment_data['publishedAt'])
            publish_date_difference = calculate_days_between_dates(
                publish_date, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            comment_info = {
                'comment': comment,
                'like_count': like_count,
                'profile_image_url': profile_image_url,
                'author_name': author_name,
                'publish_date': publish_date,
                'publish_time_difference': publish_date_difference
            }
            print(comment_info)
            comments.append(comment_info)

        nextPageToken = response.get('nextPageToken')
        if len(comments) >= max_comment_results:
            break

    return comments[:max_comment_results]

def get_video_thumbnail_medium(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        if len(video_response['items']) == 0:
            print('Video not found.')
            return None
        else:
            video_result = video_response['items'][0]
            video_snippet = video_result['snippet']
            print("***************")
            print(video_snippet)
            try:
                thumbnail_url = video_snippet['thumbnails']['standard']['url']
            except KeyError:
                thumbnail_url = video_snippet['thumbnails']['high']['url']
            print(f"Thumbnail URL: {thumbnail_url}")
            return thumbnail_url

    except HttpError as e:
        print('An HTTP error occurred:', e)
        return None

def process_thumbnail_img_270_480(thumbnail_url, video_id):
    response = requests.get(thumbnail_url)
    image = Image.open(BytesIO(response.content))

    original_width, original_height = image.size
    crop_width = 270
    crop_height = 480
    left = (original_width - crop_width) // 2
    top = (original_height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    cropped_image = image.crop((left, top, right, bottom))
    target_width = 270
    target_height = 480
    # ANTIALIAS was removed in Pillow 10.0.0. Now we need to use PIL.Image.LANCZOS or PIL.Image.Resampling.LANCZOS.
    resized_image = cropped_image.resize((target_width, target_height), Image.LANCZOS)

    #resized_image.show()
    path = THUMBNAIL_FOLDER + video_id + '_thumbnail.jpg'
    resized_image.save(path)

    # with open(path, 'rb') as image_file:
    #     image_data = image_file.read()
    # data_url = f'data:image/jpeg;base64,{image_data.hex()}'
    # print(data_url)
    # return data_url
    return path

#e.g. PT45s -> 45s
def process_duration(duration):
    second = duration[2:]
    return second

#e.g. 2022-08-29T18:58:01Z -> 2022-08-29 18:58:01
def process_time(time):
    new_time = time.replace('T', ' ')
    new_time = new_time.replace('Z', '')
    return new_time

def remove_hashtag(text):
    list = []
    for word in text.split():
        # new_word = lambda word: emoji.replace_emoji(word, replace='')
        if word[0] == '#':
            list.append(word)
    for hashtag in list:
        text = text.replace(hashtag, '')
    print(text)
    return text

def time_to_RFC(time):
    # print(datetime.datetime.now())
    new_time = time.isoformat("T") + "Z"
    print(new_time)
    return new_time

def test_youtube_search(query, max_result):
    search_results = youtube_search(query, max_result)
    if search_results:
        i = 0
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            # print(f"Language: {result['language']}")
            meta = get_video_metadata(result['video_id'])
            print(f"view count: {meta['statistics']['viewCount']}")
            print(f"create time: {process_time(meta['snippet']['publishedAt'])}")
            print('---')
    else:
        print('No search results found.')

def test_youtube_search_publish_date(query, publishedAfter, publishedBefore, max_result):
    search_results = youtube_search_publish_date(query, publishedAfter, publishedBefore, max_result)
    if search_results:
        i = 0
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            # print(f"Language: {result['language']}")
            meta = get_video_metadata(result['video_id'])
            print(f"view count: {meta['statistics']['viewCount']}")
            print(f"create time: {process_time(meta['snippet']['publishedAt'])}")
            print('---')
    else:
        print('No search results found.')

def calculate_days_between_dates(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
    days_difference = (end_date - start_date).days
    return days_difference

if __name__ == '__main__':
    # test_youtube_search('film', 50)
    get_video_metadata('jyXvd6UFg6Q')
    #remove_hashtag('The end 😂😂#fail #fails #fun #funny #funnyvideo #funnyvideos #failvideo #failarmy #funnyfail #fyp')
    # publishedAfter = '2023-07-24T00:00:00Z'
    # publishedBefore = '2023-08-01T00:00:00Z'
    # test_youtube_search_publish_date('', publishedAfter, publishedBefore, 50)

    #process_thumbnail_img_100_180(get_video_thumbnail_medium('qGoBgm5DMuw'), 'qGoBgm5DMuw')
    start_date_str = '2023-08-15 08:00:00'
    end_date_str = '2023-08-17 11:00:00'
    # days_difference = calculate_days_between_dates(start_date_str, end_date_str)
    # print(days_difference)
    # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
