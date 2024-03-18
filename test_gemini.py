import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from serpapi import GoogleSearch
API_KEY = 'AIzaSyDBBbmSa1oYutyGM6x7HQhKI87HYPV-5f8' #shorts project
# API_KEY = 'AIzaSyDD56062udoEeGQ5pRkEfxKXQ7IPCRYMEs' #test

# prompt = "Give me 10 user-interested keywords from those YouTube shorts, make the keyword list in json format:"\
# "TOP SONGS THIS WEEK MIX 🎶 TODAY'S TOP MUSIC 2024 🎶 POPULAR HITS 2024"\
# "4evr thankful I hung out in Hollywood that morning 💖 @CrashAdams are truly the best!"\
# "𝐇𝐞𝐲, 𝐒𝐓𝐑𝐀𝐍𝐆𝐄𝐑🦇❤️ #Shorts #선미 #SUNMI #STRANGER #STRANGER_Challenge"\
# "New Shelf For My Cat #cat"\
# "Crazy Cat Coloring - Unleash Your Creativity With These Adorable Feline Masterpieces"\
# "Penny not realizing she's actually married to someone else | The big bang theory #shorts #tbbt"\
# "Expectations vs Reality😱 #travel #nature #explore #instagram"\
# "5 levels of Cappuccino w/ @NickDiGiovanni"\
# "Online class be like... Watch till the end !! 😂☠️"\
# "DONT TAP YOU LIP TINT PLS 😡#makeup #lipstick #makeuptutorial"

example_result = "{ \"keywords\": [\"dewq\", \"eferfer\", \"frf\"]}"


example_title_list = "Give me 10 user-interested keywords from those YouTube videos, make the keyword list in json format:"\
"[K-Choreo 8K] VCHA 직캠 'Y.O.Universe' (VCHA Choreography) @230922"\
"선미 (SUNMI) - '열이올라요 (Heart Burn)' Music Video"\
"Goblin -Stay with me MV(OST)"\
"春晚心机被全员内涵？数十热搜，旧料全起底！逐帧开扒爆梗【春山学】白敬亭一夜翻车了？"\
"What if (G)I-DLE 'Wife' was a bit longer"\
"[MV] IVE(아이브) _ I WANT"\
"2024北京台春晚 | 小品《装不装》贾冰首演单亲爸爸，爆改儿子张驰行李箱！"\
"220619 장원영 JANGWONYOUNG 아이브 IVE 'LOVE DIVE' 4K 60P 직캠 @잠실 야구장 by DaftTaengk"\
"유연성도 노력으로 극복한 아이브 장원영ㅠㅠㅠㅠ"\
"15 Most Beautiful Chinese Actresses With and Without Makeup"\

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# genai.configure(api_key='AIzaSyAMj0xTiIE_NoyZFlntDVYj4gGLvXYrMqI')
genai.configure(api_key='AIzaSyDzKF6sjMVHIUD2I0dV08xJaivmaaVnTu0') #test

# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

model = genai.GenerativeModel('gemini-pro')



def gemini_generate_keywords(title_list):
  prompt = f"Give me 10 user-interested keyword categories (1-3 words in each category) from those YouTube videos, make the keyword list in a JSON format: {title_list}\n Example result:\"keywords\": [\"dewq\", \"eferfer\", \"frf\"]"
  print("prompt: " + prompt)
  response = model.generate_content(prompt)
  print("response.text:" + response.text)
  json_str_cleaned = response.text.replace('\n', '').replace('\r', '').replace('\t', '').replace('```', '').replace('json', '').replace('JSON', '')
  print("json_str_cleaned: " + json_str_cleaned)
  data = json.loads(json_str_cleaned)
  keywords = data["keywords"]
  print("keywords:" + json.dumps(keywords))
  if (keywords):
    return json_str_cleaned
  else: return ''

# gemini_generate_keywords(example_title_list)

def youtube_search(query):
    # query = request.form.get('query')
    print('query: ' + query)
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
      global Next_PAGE_TOKEN
      search_response = youtube.search().list(
        q=query + ' shorts',
        # q=query,
        part='snippet',
        type='video',
        order='viewCount',
        # relevanceLanguage='en',
        # videoCategoryId=42, #shorts
        videoDuration='short',
        maxResults=50,
      ).execute()
      videos_list = []
      # print(search_response)
      for search_result in search_response.get('items', []):
        print("------------------------search result--------------------")
        print(search_result)
        if search_result['id']['kind'] == 'youtube#video':
          video = {
            'title': search_result['snippet']['title'],
            'video_id': search_result['id']['videoId'],
          }
          print(video)
          videos_list.append(video)
      Next_PAGE_TOKEN = search_response.get('nextPageToken')
      print(videos_list)
      return videos_list
    except HttpError as e:
      print('An HTTP error occurred:', e)
      return None


def serp_search(query):
  print('query: ' + query)
  params = {
    "engine": "youtube",
    "search_query": query,
    "api_key": "85c96984ba5838cb5dc36a0e14c6d8c4e11d7a7c5bf6a09e9c16ab4080c15e25"
  }
  search = GoogleSearch(params)
  results = search.get_dict()
  # print("-----------------result-------------------------")
  # print("result: " + results)
  # print("-----------------end----------------------------")
  shorts_results = results["shorts_results"]
  print(shorts_results)
  return shorts_results

# youtube_search('Chinese Comedy OR Twice Dance OR How I met you mother OR makeup vlog OR how to cook steak')
# youtube_search('Chinese Comedy | how to cook steak')
# youtube_search('how to cook steak | how I met your mother')
# youtube_search('how I met your mother')
#serp_search('Chinses Comedy OR Twice Dance OR How I met you mother OR makeup vlog OR how to cook steak')
# serp_search('cats OR cat coloring OR funny animals OR travel OR nature OR explore OR cappuccino OR online class OR makeup tutorial OR lip tint')
# serp_search('travel')