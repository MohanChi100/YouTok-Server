import json
import math
import re
import spacy
from nltk.corpus import stopwords
import pytextrank


def get_results(results, limit):
    result_list = []
    tmpCount = 0
    for item in results:
      if tmpCount == limit:
        break
      result_list.append(item)
      tmpCount+=1

    return result_list

def print_result(results, header):
  print("----------" + header + "------------")
  for item in results:
    print(item)
  print("")

# Function to diversify results by comparing substrings manually
def diversify(result):
  new_result = []
  #Testing for uniqueness of words - discard if an existing entry shares a word
  for item in result:
    match = False
    item_split = item.split(" ")
    for res in new_result:
      res_split = res.split(" ")
      for word in item_split:
        if word in res_split:
          match = True
          break
      if match:
        break

    if not match:
      new_result.append(item)

  #removing duplicate words from the same entry, i.e "porsche porsche" -> "porsche"
  for i in range(len(new_result)):
    item_split = new_result[i].split(" ")
    item_split.reverse()
    for word in item_split:
      if item_split.count(word) > 1:
        item_split.remove(word)

    item_split.reverse()
    replace = ""
    for item in item_split:
      replace += item + " "

    replace = replace[0:len(replace) -1]
    new_result[i] = replace


  # removing plural words
  for word1 in new_result:
      for word2 in new_result:
        # Remove plurals of an already present word
        if (word1 + "s" == word2):
          new_result.remove(word2)
        # Remove a plural word if its singular is in another word
        # elif word1.endswith("s") and word1 in word2:
        #   new_result.remove(word1)

  return new_result


# ----------------Pre-processing and splitting the data --------------------

def processFile(filename):

  f = open(filename, encoding='utf-8')
  data = json.load(f)

  title_list = []
  hashtag_list = []

  for elem in data:
      if 'details' in elem:
          if elem['details'][0]['name'] == 'From Google Ads':
              continue

      title = re.sub("[^a-zA-Z0-9# ]", '', elem['title'])
      title = title[8:]
      while True:
          if '#' not in title:
              break
          index = title.index('#')
          stop = index + 1
          includeEnd = True
          for i in range(index + 1, len(title), 1):
              if i == len(title) - 1:
                  includeEnd = False
              elif title[i] == '#' or title[i] == ' ':
                  stop = i
                  break

          hashtag = title[index + 1:stop] if includeEnd else title[index + 1:]

          # trying to remove only numbers in titles such as football games
          # ex: #11, #5
          hashtagDup = hashtag
          hashtagNoNum = re.sub("[^0-9]", '', hashtagDup)
          hashtagNoNum = hashtagNoNum.strip()
          if hashtagNoNum == '':
              hashtag_list.append(hashtag.lower())

          title = title[0:index] + title[stop:] if includeEnd else title[0:index]

      title_list.append(title.lower())

  allTitles = ""
  for title in title_list:
      allTitles += " " + title

  # remove numbers and stopwords
  title_split = allTitles.split()
  for word in title_split:
      word = word.lower()
      word = word.strip()
      # removing common/filler words, "the", words of length 2 or less since those
      # are usually just filler, and numbers since the majority are meaningless.
      exclude = ['the', 'video', 'videos', 'no']
      if word in stopwords.words("english") or word in exclude or len(word) <= 2 or word.isnumeric():
          title_split = [elem for elem in title_split if elem != word]



  #----------- Ranking --------------------


  # Finding the most common words in the titles
  # Sorting list by frequency and removing duplicates
  title_split = sorted(set(title_split), key=lambda title: title_split.count(title), reverse=True)

  # Sorting hashtag list by freq
  hashtag_list = sorted(set(hashtag_list), key=lambda hashtag: hashtag_list.count(hashtag), reverse=True)
  hashtag_list = get_results(hashtag_list, 15)


  # Text Rank
  nlp = spacy.load("en_core_web_sm", max_length=3000000)
  nlp.add_pipe("textrank")
  doc = nlp(allTitles)

  result = {}
  for phrase in doc._.phrases:
      result[phrase.text] = phrase.rank


  # Sorts the dictionary by phrase.rank
  textrank_result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
  textrank_result = diversify(textrank_result)
  textrank_result = get_results(textrank_result, 20)

  return (textrank_result, hashtag_list)

def GetKeywordsFromJsonData(jsondata):

  # f = open(filename, encoding='utf-8')
  # data = json.load(f)

  print("!!!!!!!!!!GetKeywordsFromJsonData!!!!!!!!")
  data = jsondata

  title_list = []
  hashtag_list = []

  for elem in data:
      if 'details' in elem:
          if elem['details'][0]['name'] == 'From Google Ads':
              continue

      if elem is not None and 'title' in elem:
        title = re.sub("[^a-zA-Z0-9# ]", '', elem['title'])
      else:
        title = ""
      title = title[8:]
      while True:
          if '#' not in title:
              break
          index = title.index('#')
          stop = index + 1
          includeEnd = True
          for i in range(index + 1, len(title), 1):
              if i == len(title) - 1:
                  includeEnd = False
              elif title[i] == '#' or title[i] == ' ':
                  stop = i
                  break

          hashtag = title[index + 1:stop] if includeEnd else title[index + 1:]

          # trying to remove only numbers in titles such as football games
          # ex: #11, #5
          hashtagDup = hashtag
          hashtagNoNum = re.sub("[^0-9]", '', hashtagDup)
          hashtagNoNum = hashtagNoNum.strip()
          if hashtagNoNum == '':
              hashtag_list.append(hashtag.lower())

          title = title[0:index] + title[stop:] if includeEnd else title[0:index]

      title_list.append(title.lower())

  allTitles = ""
  for title in title_list:
      allTitles += " " + title

  # remove numbers and stopwords
  title_split = allTitles.split()
  for word in title_split:
      word = word.lower()
      word = word.strip()
      # removing common/filler words, "the", words of length 2 or less since those
      # are usually just filler, and numbers since the majority are meaningless.
      exclude = ['the', 'video', 'videos', 'no']
      if word in stopwords.words("english") or word in exclude or len(word) <= 2 or word.isnumeric():
          title_split = [elem for elem in title_split if elem != word]



  #----------- Ranking --------------------


  # Finding the most common words in the titles
  # Sorting list by frequency and removing duplicates
  title_split = sorted(set(title_split), key=lambda title: title_split.count(title), reverse=True)

  # Sorting hashtag list by freq
  hashtag_list = sorted(set(hashtag_list), key=lambda hashtag: hashtag_list.count(hashtag), reverse=True)
  hashtag_list = get_results(hashtag_list, 15)


  # Text Rank
  nlp = spacy.load("en_core_web_sm")
  nlp.add_pipe("textrank")
  # if len(allTitles) > 1000000:
  #   allTitles=allTitles[:100000]
  doc = nlp(allTitles)

  result = {}
  for phrase in doc._.phrases:
      result[phrase.text] = phrase.rank


  # Sorts the dictionary by phrase.rank
  textrank_result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
  textrank_result = diversify(textrank_result)
  textrank_result = get_results(textrank_result, 20)

  result_list = []
  for textrank in textrank_result:
    result_list.append(textrank)
  for hashtag in hashtag_list:
    result_list.append(hashtag)

  return result_list


def getKeywords(filename):
  return processFile(filename)[0]

def getHashtags(filename):
  return processFile(filename)[1]



# print_result(getKeywords("watch-history.json"), "textrank")
# print_result(getHashtags("watch-history.json"), "Hashtags")