# from math import nextafter
from flask import Flask, request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy import or_
from flask_cors import CORS
import video
import os
import keyword_extraction
from datetime import datetime, timedelta
import test_gemini
import random



import asyncio
# import websockets
import threading
from flask_socketio import SocketIO, emit
from flask import render_template

app = Flask(__name__)
# cors = CORS(app)
# socketio = SocketIO(app)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*") 

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'test'
#app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
#app.config['MYSQL_DATABASE_DB'] = 'YouTok' #database name
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:cmH19960911!@localhost:13306/YouTok'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

@socketio.on('connect')
def handle_connect():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    print('Client connected: ' + formatted_datetime)

@socketio.on('disconnect', namespace='/test')
def handle_disconnect():
    print('User disconnected')

@app.route('/notify_disconnect')
def notify_disconnect():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    print('User is leaving the website, notification from unload:' + formatted_datetime)
    return 'OK'

#test functions:
def test_store_one_video_meta_data(vid):
    result = video.get_video_metadata(vid)
    if result:
        meta_data = {
            'duration': video.process_duration(result['contentDetails']['duration']),
            'category': result['snippet']['categoryId'],
            'create_time': video.process_time(result['snippet']['publishedAt']),
            'view_count': result['statistics']['viewCount'],
            'creator': result['snippet']['channelTitle']
        }
        print(f"duration: {meta_data['duration']}")
        print(f"category: {meta_data['category']}")
        print(f"create_time: {meta_data['create_time']}")
        print(f"view_count: {meta_data['view_count']}")
        print(f"creator: {meta_data['creator']}")

        new_video = Video(vid=vid, duration=meta_data['duration'], category=meta_data['category'],
                          create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                          creator=meta_data['creator'])
        db.session.merge(new_video)
        db.session.commit()

def test_store_one_like_video_meta_data(vid, keyword, uid, title):
    result = video.get_video_metadata(vid)
    if result:
        meta_data = {
            'duration': video.process_duration(result['contentDetails']['duration']),
            'category': result['snippet']['categoryId'],
            'create_time': video.process_time(result['snippet']['publishedAt']),
            'view_count': result['statistics']['viewCount'],
            'creator': result['snippet']['channelTitle'],
            'title': title
        }
        print(f"duration: {meta_data['duration']}")
        print(f"category: {meta_data['category']}")
        print(f"create_time: {meta_data['create_time']}")
        print(f"view_count: {meta_data['view_count']}")
        print(f"creator: {meta_data['creator']}")
        print(f"title: {title}")

        new_like_video = LikeVideo(vid=vid, duration=meta_data['duration'], category=meta_data['category'],
                          create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                          creator=meta_data['creator'], title=meta_data['title'], uid=uid, keyword=keyword)
        db.session.merge(new_like_video)
        db.session.commit()

def test_get_and_store_video_meta_data(query, publishedAfter, publishedBefore):
    # search_results = video.youtube_search(search_query, 50)
    search_results = video.youtube_search_publish_date(query,publishedAfter, publishedBefore, 50)

    video_id_list = []
    i = 0
    if search_results:
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print('---')
            video_id_list.append(result['video_id'])
            test_store_one_video_meta_data(result['video_id'])
    else:
        print('No search results found.')

def test_get_and_store_like_video_meta_data(query, publishedAfter, publishedBefore, uid, resultCount=10):
    # search_results = video.youtube_search(search_query, 50)
    search_results = video.youtube_search_publish_date(query,publishedAfter, publishedBefore, resultCount)

    video_id_list = []
    i = 0
    if search_results:
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print('---')
            video_id_list.append(result['video_id'])
            test_store_one_like_video_meta_data(result['video_id'], query, uid, result['title'])
    else:
        print('No search results found.')

def add_new_user(uid, password, next_page_token = ''):
    new_user = UserLogin(uid=uid, password=password, next_page_token=next_page_token)
    db.session.merge(new_user)
    db.session.commit()

def add_keyword(uid, keyword):
    new_keyword = Keyword(uid=uid, keyword=keyword)
    db.session.merge(new_keyword)
    # print('here!!!!!')
    db.session.commit()

def UseKeywordToQureyVideo(query, publishedAfter, publishedBefore, uid, resultCount):
    search_results = video.youtube_search_publish_date(query,publishedAfter, publishedBefore, resultCount)
    video_id_list = []
    i = 0
    if search_results:
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print('---')
            video_id_list.append(result['video_id'])
            result_1 = video.get_video_metadata(result['video_id'])

            if result_1:
                meta_data = {
                    'duration': video.process_duration(result_1['contentDetails']['duration']),
                    'category': result_1['snippet']['categoryId'],
                    'create_time': video.process_time(result_1['snippet']['publishedAt']),
                    'view_count': result_1['statistics']['viewCount'],
                    'creator': result_1['snippet']['channelTitle'],
                    'title': result['title']
                }
                new_video = Video(vid=result['video_id'], duration=meta_data['duration'], category=meta_data['category'],
                          create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                          creator=meta_data['creator'], title=meta_data['title'])
                db.session.merge(new_video)
                db.session.commit()
        return video_id_list
    else:
        print('No search results found.')
        return []

def UseKeywordToQureyVideoByPageToken(query, uid, pageToken, resultCount):
    search_results, next_page_token = video.youtube_search(query, pageToken, resultCount)
    video_id_list = []
    likeCount_list = []
    commentCount_list = []
    i = 0
    if search_results:
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print('---')
            video_id_list.append(result['video_id'])
            
            result_1 = video.get_video_metadata(result['video_id'])
            
            if result_1:
                if 'statistics' in result_1 and 'likeCount' in result_1['statistics']:
                    likeCount_list.append(result_1['statistics']['likeCount'])
                else:
                    likeCount_list.append(0)
                if 'statistics' in result_1 and 'commentCount' in result_1['statistics']:
                    commentCount_list.append(result_1['statistics']['commentCount'])
                else:
                    commentCount_list.append(0)
                
                meta_data = {
                    'duration': video.process_duration(result_1['contentDetails']['duration']),
                    'category': result_1['snippet']['categoryId'],
                    'create_time': video.process_time(result_1['snippet']['publishedAt']),
                    'view_count': result_1['statistics']['viewCount'],
                    'creator': result_1['snippet']['channelTitle'],
                    'title': result['title']
                }
                new_video = Video(vid=result['video_id'], duration=meta_data['duration'], category=meta_data['category'],
                          create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                          creator=meta_data['creator'], title=meta_data['title'])
                db.session.merge(new_video)
                db.session.commit()
        if next_page_token:
            current_user = UserLogin.query.get(uid)
            if current_user:
                current_user.next_page_token = next_page_token
                db.session.merge(current_user)
                db.session.commit()
        return video_id_list, likeCount_list, commentCount_list
    else:
        print('No search results found.')
        return [], [], []

def GetKeywordListByUID(uid):
    keyword_list = []
    print("*************GetKeywordListByUID*************: " + uid)
    result = Keyword.query.filter_by(uid=uid).all()
    print("@@@@@@@@@@@@@@GetKeywordListByUID@@@@@@@@@@@@@@@")
    if result:
        print("!!!!!!!!!!!!GetKeywordListByUID!!!!!!!!!!!!")
        for keyword_item in result:
            keyword_list.append(keyword_item.keyword)
        print(keyword_list)
        return keyword_list
    else:
        return keyword_list

def GetUserNextPageToken(uid):
    result = UserLogin.query.filter_by(uid=uid).first()
    if result.next_page_token:
        return result.next_page_token
    else:
        return ''


class Keyword(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    keyword = db.Column(db.String(100), primary_key=True)

    def __repr__(self):
        return f"<Keyword: {self.uid}>"

class Treatment(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    playmode = db.Column(db.Text)
    week_1 = db.Column(db.Text)
    week_2 = db.Column(db.Text)

    def __repr__(self):
        return f"<Treatment: {self.uid}>"

class Video(db.Model):
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vid = db.Column(db.String(100), primary_key=True)
    duration = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    create_time = db.Column(db.DateTime(timezone=True), nullable=True)
    view_count = db.Column(db.Integer)
    creator = db.Column(db.Text)
    title = db.Column(db.Text)

    def __repr__(self):
        return f"<Video: {self.vid}>"

class VideoInteraction(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    vid = db.Column(db.String(100), primary_key=True)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    start_how = db.Column(db.Text)
    end_how = db.Column(db.Text)
    liked = db.Column(db.Boolean, server_default=expression.false())
    liked_datetime = db.Column(db.DateTime(timezone=True))
    disliked = db.Column(db.Boolean, server_default=expression.false())
    disliked_datetime = db.Column(db.DateTime(timezone=True))
    share = db.Column(db.Boolean, server_default=expression.false())
    share_datetime = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return f"<VideoInteraction: {self.uid}, {self.vid}>"

class User(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    age = db.Column(db.Integer)
    race = db.Column(db.Text)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)

    def __repr__(self):
        return f"<User: {self.uid}>"

class Preference(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    like_1 = db.Column(db.Text)
    like_2 = db.Column(db.Text)
    like_3 = db.Column(db.Text)
    dislike_1 = db.Column(db.Text)
    dislike_2 = db.Column(db.Text)
    dislike_3 = db.Column(db.Text)

    def __repr__(self):
        return f"<Preference: {self.uid}>"

class Pause(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(100))
    vid = db.Column(db.String(100))
    is_pause = db.Column(db.Boolean)
    time = db.Column(db.Text)

class Comment(db.Model):
    vid_no = db.Column(db.String(100), primary_key=True)
    text = db.Column(db.Text)

class CommentInteraction(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    vid = db.Column(db.String(100), primary_key=True)
    # like = db.Column(db.Boolean, server_default=expression.false())
    # dislike = db.Column(db.Boolean, server_default=expression.false())
    new_comment = db.Column(db.Text)

class UserLogin(db.Model):
    uid = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))
    next_page_token = db.Column(db.String(100))

class LikeVideo(db.Model):
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vid = db.Column(db.String(100), primary_key=True)
    duration = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    create_time = db.Column(db.DateTime(timezone=True), nullable=True)
    view_count = db.Column(db.Integer)
    creator = db.Column(db.Text)
    title = db.Column(db.Text)
    uid = db.Column(db.Text)
    keyword = db.Column(db.Text)

    def __repr__(self):
        return f"<Video: {self.vid}>"


class SurveyResponse(db.Model):
    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(100))
    date_submitted = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    session_duration_minutes = db.Column(db.Integer, nullable=False)
    video_count = db.Column(db.Integer, nullable=False)
    video_characters = db.Column(db.Text, nullable=True)
    last_video_description = db.Column(db.Text, nullable=True)
    session_keywords = db.Column(db.Text, nullable=True)
    satisfaction_rating = db.Column(db.Integer, nullable=False)
    interest_keywords = db.Column(db.Text, nullable=True)
    favorite_video_description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<SurveyResponse: {self.response_id}>"


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/saveSurveyResponse', methods = ['POST'])
def saveSurveyResponse():
    print("Received data:", request.json)
    uid = request.json.get('uid')
    print("uid: ", uid)
    session_duration_minutes = int(request.json.get('session_duration_minutes', 0))
    video_count = int(request.json.get('video_count', 0))
    video_characters = request.json.get('video_characters', '')
    last_video_description = request.json.get('last_video_description', '')
    session_keywords = request.json.get('session_keywords', '')
    satisfaction_rating = int(request.json.get('satisfaction_rating', 0))
    interest_keywords = request.json.get('interest_keywords', '')
    favorite_video_description = request.json.get('favorite_video_description', '')

    # Create a new survey response object
    new_response = SurveyResponse(
        uid=uid,
        session_duration_minutes=session_duration_minutes,
        video_count=video_count,
        video_characters=video_characters,
        last_video_description=last_video_description,
        session_keywords=session_keywords,
        satisfaction_rating=satisfaction_rating,
        interest_keywords=interest_keywords,
        favorite_video_description=favorite_video_description
    )

    # Add the new object to the database session and commit it
    db.session.add(new_response)
    db.session.commit()

    # Return a success response
    return jsonify({'message': 'Survey response saved successfully!'})

@app.route('/QueryVideoByUID', methods = ['GET'])
def QueryVideoByUID():
    uid = request.args.get('uid')
    # publishedAfter = request.args.get('publishedAfter')
    # publishedBefore = request.args.get('publishedBefore')
    resultCount = request.args.get('resultCount')

    video_id_list = []
    likeCount_list = []
    commentCount_list = []
    query = ''
    next_page_token = GetUserNextPageToken(uid)
    keyword_list = GetKeywordListByUID(uid)
    for i, keyword in enumerate(keyword_list):
        query += keyword
        if i < len(keyword_list) - 1:
            query += '|'

    # result_list = UseKeywordToQureyVideo(query, publishedAfter, publishedBefore, uid, resultCount)
    result_list, likeCount_list, commentCount_list = UseKeywordToQureyVideoByPageToken(query, uid, next_page_token, resultCount)
    data = {
        "video_id_list": [],
        "likeCount_list": [],
        "commentCount_list": []
    }
    for result1 in result_list:
        data["video_id_list"].append(result1)
    for result2 in likeCount_list:
        data["likeCount_list"].append(result2)
    for result3 in commentCount_list:
        data["commentCount_list"].append(result3)
    
    return data

@app.route('/VerifyUser', methods = ['POST'])
def VerifyUser():
    uid = request.form.get('uid')
    password = request.form.get('password')
    print(uid)
    print(password)
    userlogin = UserLogin.query.filter_by(uid=uid).first()
    if (userlogin and userlogin.password == password):
        return 'true'
    else:
        return 'false'

@app.route('/GetTreatment', methods = ['GET'])
def GetTreatmentByUID():
    uid = request.args.get('uid')
    print("uid: " + uid)
    treatment = Treatment.query.filter_by(uid=uid).first()
    if treatment:
        print("get treatment!!!!!!!")
        user_treatment = {
            'playmode': treatment.playmode,
            'week_1': treatment.week_1,
            'week_2': treatment.week_2}
        print(user_treatment)
        return user_treatment
    else:
        return ''


@app.route('/SaveVideoData', methods = ['POST'])
def VideoDataReceived():
    vid = request.form['vid']
    # duration = request.form['duration']
    # category = request.form['category']
    # create_time = request.form['create_time']
    # view_count = request.form['view_count']
    # creator = request.form['creator']
    result = video.get_video_metadata(vid)
    if result:
        meta_data = {
            'duration': video.process_duration(result['contentDetails']['duration']),
            'category': result['snippet']['categoryId'],
            'create_time': video.process_time(result['snippet']['publishedAt']),
            'view_count': result['statistics']['viewCount'],
            'creator': result['snippet']['channelTitle']
        }
        print(f"duration: {meta_data['duration']}")
        print(f"category: {meta_data['category']}")
        print(f"create_time: {meta_data['create_time']}")
        print(f"view_count: {meta_data['view_count']}")
        print(f"creator: {meta_data['creator']}")

        new_video = Video(vid=vid, duration=meta_data['duration'], category=meta_data['category'],
                          create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                          creator=meta_data['creator'])
        db.session.merge(new_video)
        db.session.commit()
        return 'Video information is stored'
    else:
        return 'Fail to store the video information'

@app.route('/SaveVideoInteraction', methods = ['POST'])
def VideoInteractionReceived():
    uid = request.form['uid']
    vid = request.form['vid']
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    start_how = request.form.get('start_how')
    end_how = request.form.get('end_how')
    liked = request.form.get('liked', 'false') == 'true'
    liked_datetime = request.form.get('liked_datetime')
    disliked = request.form.get('disliked', 'false') == 'true'
    disliked_datetime = request.form.get('disliked_datetime')
    share = request.form.get('share', 'false') == 'true'
    share_datetime = request.form.get('share_datetime')

    def change_interaction_props():
        video_interaction = db.session.scalars(
            select(VideoInteraction)
            .filter(
                VideoInteraction.uid == uid,
                VideoInteraction.vid == vid,
            )
            .with_for_update()
        ).one()

        for key, value in request.values.items():
            if value is not None and value != '':
                if value == 'true':
                    setattr(video_interaction, key, True)
                elif value == 'false':
                    setattr(video_interaction, key, False)
                else:
                    setattr(video_interaction, key, value)

    video_interaction = db.session.get(VideoInteraction, (uid, vid))
    if video_interaction is None:
        new_video_interation = VideoInteraction(uid=uid, vid=vid, start_time=start_time, end_time=end_time,
                                                start_how=start_how, end_how=end_how,
                                                liked=liked, liked_datetime=liked_datetime,
                                                disliked=disliked, disliked_datetime=disliked_datetime, 
                                                share=share, share_datetime=share_datetime)
        try:
            db.session.add(new_video_interation)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            change_interaction_props()
    else:
        change_interaction_props()
    db.session.commit()
    return 'Video interaction is stored'

@app.route('/SaveUserInformation', methods = ['POST'])
def UserInformationReceived():
    uid = request.form['uid']
    age = int(request.form['age'])
    race = request.form['race']
    gender = request.form['gender']
    education = request.form['education']
    experience = request.form['experience']
    new_user = User(uid=uid, age=age, race=race, gender=gender,
                    education=education, experience=experience)
    db.session.merge(new_user)
    db.session.commit()
    return 'User Information is stored'


@app.route('/SaveUserPreference', methods = ['POST'])
def UserPreferenceReceived():
    uid = request.form['uid']
    like_1 = request.form['like_1']
    like_2 = request.form['like_2']
    like_3 = request.form['like_3']
    dislike_1 = request.form['dislike_1']
    dislike_2 = request.form['dislike_2']
    dislike_3 = request.form['dislike_3']
    new_preference = Preference(uid=uid, like_1=like_1, like_2=like_2, like_3=like_3,
                                dislike_1=dislike_1, dislike_2=dislike_2, dislike_3=dislike_3)
    db.session.merge(new_preference)
    db.session.commit()
    return 'User Preference is stored'

@app.route('/GetLikeVideoList', methods = ['GET'])
def GetLikeVideoList():
    # uid = request.form['uid']
    uid = request.values.get('uid')
    # print('uid:'+ uid)
    preference = Preference.query.filter_by(uid=uid).first()
    # print('uid: ' + preference.uid+', like_1:' + preference.like_1
    #       + ', like_2:' + preference.like_2 + ', like_3:' + preference.like_3
    #       + ', dislike_1:' + preference.dislike_1 + ', dislike_2:' + preference.dislike_2
    #       + ', dislike_3:' + preference.dislike_3)

    query = preference.like_1 + '|' + preference.like_2 + '|' + preference.like_3
    video_list = []
    result_list = video.youtube_search(query)
    if result_list:
        for result in result_list:
            # print(f"Title: {result['title']}")
            # print(f"Video ID: {result['video_id']}")
            video_list.append(result['video_id'])
            # print('---')
    else:
        print('No search results found.')

    return video_list

@app.route('/GetLikeVideoListByCategory', methods = ['GET'])
def GetLikeVideoListByCategory():
    uid = request.values.get('uid')
    preference = Preference.query.filter_by(uid=uid).first()
    print('uid: ' + preference.uid+', like_1:' + preference.like_1
          + ', like_2:' + preference.like_2 + ', like_3:' + preference.like_3
          + ', dislike_1:' + preference.dislike_1 + ', dislike_2:' + preference.dislike_2
          + ', dislike_3:' + preference.dislike_3)

    video_ids_list = []
    video_all = Video.query.filter(or_(
        Video.category == preference.like_1,
        Video.category == preference.like_2,
        Video.category == preference.like_3
    )).all()
    if video_all:
        for video in video_all:
            video_ids_list.append(video.vid)
        print(video_ids_list)
        return video_ids_list
    else:
        return video_ids_list

@app.route('/GetAllVideoID', methods = ['GET'])
def GetAllVideoIDs():
    video_all = Video.query.with_entities(Video.vid).all()
    if video_all:
        video_ids_list = [video_id[0] for video_id in video_all]
        print(video_ids_list)
        return video_ids_list
    else:
        return []

@app.route('/GetVideoIDByCategory', methods = ['GET'])
def GetVideoIDByCategory():
    category = request.values.get('category')
    video_ids_list = []
    video_all = Video.query.filter_by(category=category).all()
    if video_all:
        for video in video_all:
            video_ids_list.append(video.vid)
        print(video_ids_list)
        return video_ids_list
    else:
        return video_ids_list

@app.route('/GetVideoMetaData', methods = ['GET'])
def GetVideoMetaData():
    # uid = request.form['uid']
    vid = request.values.get('vid')
    # print('vid:' + vid)
    result = video.get_video_metadata(vid)
    # print('here!!!!!!!')
    if result:
        meta_data = {
            'duration': video.process_duration(result['contentDetails']['duration']),
            'category': result['snippet']['categoryId'],
            'create_time': result['snippet']['publishedAt'],
            'view_count': result['statistics']['viewCount'],
            'creator': result['snippet']['channelTitle']
        }
        # print(f"Title: {meta_data['duration']}")
        # print(f"Title: {meta_data['create_time']}")
        # print(f"Title: {meta_data['view_count']}")
        # print(f"Title: {meta_data['creator']}")

        return meta_data
    else:
        print('No video data found.')
    return []

@app.route('/SavePauseData', methods = ['POST'])
def SavePauseData():
    uid = request.form['uid']
    vid = request.form['vid']
    is_pause = request.form.get('is_pause', 'false') == 'true'
    time = request.form['time']
    new_pause = Pause(uid=uid, vid=vid, is_pause=is_pause, time=time)
    db.session.add(new_pause)
    db.session.commit()
    return 'User Information is stored'

@app.route('/GetVideoComment', methods = ['GET'])
def GetVideoComment():
    vid = request.values.get('vid')
    comment_list = video.get_video_comments(vid)
    index = 0
    if comment_list:
        for comment_info in comment_list:
            vid_no = vid + '_' + str(index)
            new_comment = Comment(vid_no=vid_no, text=comment_info['comment'])
            db.session.merge(new_comment)
            db.session.commit()
            index = index + 1
        print('comment_list has been stored')
        return comment_list
    else:
        print('No video comment found.')
    return []

@app.route('/SaveVideoCommentInteraction', methods = ['POST'])
def SaveVideoCommentInteraction():
    uid = request.values.get('uid')
    vid = request.values.get('vid')
    comment_id = request.values.get('comment_id')
    vid_no = vid + '_' + comment_id
    like = request.values.get('like')
    dislike = request.values.get('dislike')

    def change_comment_interaction_props():
        comment_interaction = db.session.scalars(
            select(CommentInteraction)
            .filter(
                CommentInteraction.uid == uid,
                CommentInteraction.vid_no == vid_no,
            )
            .with_for_update()
        ).one()

        for key, value in request.values.items():
            if value is not None and value != '':
                if value == 'true':
                    setattr(comment_interaction, key, True)
                elif value == 'false':
                    setattr(comment_interaction, key, False)
                else:
                    setattr(comment_interaction, key, value)

    comment_interaction = db.session.get(CommentInteraction, (uid, vid_no))
    if comment_interaction is None:
        new_comment_interaction = CommentInteraction(uid=uid, vid_no=vid_no, like=False, dislike=False)

        if like is not None:
            new_comment_interaction.like = like.lower() == 'true'
        if dislike is not None:
            new_comment_interaction.dislike = dislike.lower() == 'true'

        try:
            db.session.add(new_comment_interaction)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            change_comment_interaction_props()
    else:
        change_comment_interaction_props()

    db.session.commit()
    return 'Comment interaction is stored'

@app.route('/GetThumbnailList', methods = ['GET'])
def GetThumbnailList():
    print('!!!!!!!!!call GetThumbnailList')

    uid = request.values.get('uid')
    resultCount = request.values.get('resultCount')

    video_id_list = []
    thumbnail_list = []
    query = ''
    next_page_token = GetUserNextPageToken(uid)
    keyword_list = GetKeywordListByUID(uid)
    for i, keyword in enumerate(keyword_list):
        query += keyword
        if i < len(keyword_list) - 1:
            query += ' |'

    # result_list = UseKeywordToQureyVideo(query, publishedAfter, publishedBefore, uid, resultCount)
    result_list, likeCount_list, commentCount_list = UseKeywordToQureyVideoByPageToken(query, uid, next_page_token, resultCount)
    for result in result_list:
        video_id_list.append(result)

    if video_id_list:
        for i, video_id in enumerate(video_id_list):
            # thumbnail_path = video.process_thumbnail_img_270_480(video.get_video_thumbnail_medium(video_1.vid), video_1.vid)
            # thumbnail_list.append({'thumbnail_path': thumbnail_path, 'video_id': video_1.vid})
            video_item = Video.query.filter(Video.vid == video_id).first()
            thumbnail_path = video.get_video_thumbnail_medium(video_item.vid)
            thumbnail_list.append({
                'thumbnail_path': thumbnail_path,
                'video_id': video_item.vid,
                'title': video_item.title,
                'creator': video_item.creator,
                'viewcount': video_item.view_count,
                'likeCount': likeCount_list[i],
                'commentCount': commentCount_list[i]})
        print(thumbnail_list)
        return thumbnail_list
    else:
        return thumbnail_list

@app.route('/SaveUserNewComment', methods = ['POST'])
def UserCommentReceived():
    uid = request.form['uid']
    vid = request.form['vid']
    new_comment = request.form['new_comment']
    new_comment_store = CommentInteraction(uid=uid, vid=vid, new_comment=new_comment)
    db.session.merge(new_comment_store)
    db.session.commit()
    return 'User Comment is stored'

@app.route('/GetLikeVideoListInLikeVideoTable', methods = ['GET'])
def GetLikeVideoListInLikeVideoTable():
    uid = request.values.get('uid')

    video_ids_list = []
    video_all = LikeVideo.query.filter(LikeVideo.uid == uid).all()
    if video_all:
        for video in video_all:
            video_ids_list.append(video.vid)
        print(video_ids_list)
        return video_ids_list
    else:
        return video_ids_list

@app.route('/GetThumbnailListInLikeTable', methods = ['GET'])
def GetThumbnailListInLikeTable():
    uid = request.values.get('uid')
    thumbnail_list = []
    video_all = LikeVideo.query.filter(LikeVideo.uid == uid).all()
    if video_all:
        for video_1 in video_all:
            # thumbnail_path = video.process_thumbnail_img_270_480(video.get_video_thumbnail_medium(video_1.vid), video_1.vid)
            thumbnail_path = video.get_video_thumbnail_medium(video_1.vid)
            thumbnail_list.append({
                'thumbnail_path': thumbnail_path,
                'video_id': video_1.vid,
                'title': video_1.title,
                'creator': video_1.creator,
                'viewcount': video_1.view_count})
        print(thumbnail_list)
        return thumbnail_list
    else:
        return thumbnail_list

@app.route('/AddUser', methods = ['POST'])
def add_new_user_adduser():
    uid = request.form['uid']
    password = request.form['password']
    next_page_token = request.form['next_page_token']
    new_user = UserLogin(uid=uid, password=password, next_page_token=next_page_token)
    db.session.merge(new_user)
    db.session.commit()
    return 'user added!'

@app.route('/AddKeyword', methods = ['POST'])
def add_keyword_addkeyword():
    uid = request.form['uid']
    keyword = request.form['keyword']
    new_keyword = Keyword(uid=uid, keyword=keyword)
    db.session.merge(new_keyword)
    db.session.commit()
    return 'keyword added'

@app.route('/AddVideos', methods = ['POST'])
def test_get_and_store_like_video_meta_data_addvideos():
    # search_results = video.youtube_search(search_query, 50)
    query = request.form.get('keyword')
    uid = request.form.get('uid')
    publishedAfter = request.form.get('publishedAfter')
    publishedBefore = request.form.get('publishedBefore')
    resultCount = request.form.get('resultCount')
    search_results = video.youtube_search_publish_date(query,publishedAfter, publishedBefore, resultCount)
 
    video_id_list = []
    i = 0
    if search_results:
        for result in search_results:
            i = i + 1
            print(i)
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print('---')
            video_id_list.append(result['video_id'])
            test_store_one_like_video_meta_data(result['video_id'], query, uid, result['title'])
    else:
        print('No search results found.')

@app.route('/GenerateKeywords', methods=['POST'])
def generate_keywords():
    print("@@@@@@@@@@@@@@GenerateKeywords@@@@@@@@@@@@")
    json_data = request.get_json()
    print(json_data)
    keywords = keyword_extraction.GetKeywordsFromJsonData(json_data)
    return keywords
    # else:
    #     return jsonify({'error': 'Invalid form submission'})

@app.route('/gemini_get_keywords', methods = ['POST'])
def gemini_get_keywords():
    print("!!!!!@@@@@@@")
    post_json = request.get_json()
    print(post_json['title_list'])
    result_string = ''
    for item in post_json['title_list']:
        result_string += f"{item},"
    print(result_string)
    response = test_gemini.gemini_generate_keywords(result_string)
    print("--------------!!!------------------")
    print(response)
    return response

@app.route('/youtube_search_test_api', methods = ['POST'])
def youtube_search_test_api():
    query = request.form.get('query')
    print('query from main: ' + query)
    # return [{'title': 'Marvin starts college - How I Met Your Mother #shorts', 'video_id': 'f3tCFRBC-3k'}, {'title': 'BARNEY&#39;S REVENGE  | How I met your mother #shorts #barneystinson #himym', 'video_id': 'DzEsvg5-2yE'}, {'title': 'Best Pickup Line Ever-Barney Stinson', 'video_id': 'TKhB6-G478w'}, {'title': 'ELE NÃO VEM... | How I Met Your Mother #shorts', 'video_id': 'PogYtME3C-0'}, {'title': 'when you walk in your parents room without knocking #shorts #mom #dad', 'video_id': 'd-P30p3dT78'}]
    response, Next_PAGE_TOKEN = video.youtube_search(query, None)

    # store video data
    if response:
        for result in response:
            result_1 = video.get_video_metadata(result['video_id'])
            if result_1:
                meta_data = {
                    'duration': video.process_duration(result_1['contentDetails']['duration']),
                    'category': result_1['snippet']['categoryId'],
                    'create_time': video.process_time(result_1['snippet']['publishedAt']),
                    'view_count': result_1['statistics']['viewCount'],
                    'creator': result_1['snippet']['channelTitle'],
                    'title': result['title']
                }
                new_video = Video(vid=result['video_id'], duration=meta_data['duration'],
                                  category=meta_data['category'],
                                  create_time=meta_data['create_time'], view_count=meta_data['view_count'],
                                  creator=meta_data['creator'], title=meta_data['title'])
                db.session.merge(new_video)
                db.session.commit()
    # end store video data

    return response

# get maxmium 250 videos every day for each user
@app.route('/GetEverydayVideoListForUser', methods = ['GET'])
def GetEverydayVideoListForUser():
    uid = request.args.get('uid')
    print("GetEverydayVideoListForUser #### uid: " + uid)
    keyword_list = GetKeywordListByUID(uid)

    data = {
        "video_id_list": [],
        "likeCount_list": [],
        "commentCount_list": []
    }

    for i, keyword in enumerate(keyword_list):
        result_list, likeCount_list, commentCount_list = UseKeywordToQureyVideoByPageToken(keyword, uid, None, 25)
        for result1 in result_list:
            data["video_id_list"].append(result1)
        for result2 in likeCount_list:
            data["likeCount_list"].append(result2)
        for result3 in commentCount_list:
            data["commentCount_list"].append(result3)

    # make the order random
    combined = list(zip(data["video_id_list"], data["likeCount_list"], data["commentCount_list"]))
    # Shuffle the combined list
    random.shuffle(combined)
    # Unzip the combined list back into individual lists
    data["video_id_list"], data["likeCount_list"], data["commentCount_list"] = zip(*combined)
    # Convert tuples back to lists
    data["video_id_list"] = list(data["video_id_list"])
    data["likeCount_list"] = list(data["likeCount_list"])
    data["commentCount_list"] = list(data["commentCount_list"])

    return data

# request the same video list everyday for each participant
@app.route('/GetEverydayVideoListForUserLow', methods = ['GET'])
def GetEverydayVideoListForUserLow():
    data = {
        "video_id_list": [],
        "likeCount_list": [],
        "commentCount_list": []
    }

    # Querying the first 200 Video records that are not present in the VideoInteraction table
    videos = db.session.query(Video).outerjoin(VideoInteraction, Video.vid == VideoInteraction.vid) \
        .filter(VideoInteraction.vid.is_(None)) \
        .limit(200) \
        .all()

    for video in videos:
        data["video_id_list"].append(video.vid)
        data["likeCount_list"].append(str(random.randint(20, 30000)))
        data["commentCount_list"].append(str(random.randint(20, 30000)))

    return data
@app.route('/GetEverydayVideoListForUserThumbnail', methods = ['GET'])
def GetEverydayVideoListForUserThumbnail():
    print('!!!!!!!!!call GetThumbnailList')
    uid = request.values.get('uid')

    video_id_list = []
    thumbnail_list = []

    keyword_list = GetKeywordListByUID(uid)
    data = {
        "video_id_list": [],
        "likeCount_list": [],
        "commentCount_list": []
    }

    for i, keyword in enumerate(keyword_list):
        result_list, likeCount_list, commentCount_list = UseKeywordToQureyVideoByPageToken(keyword, uid, None, 25)
        for result1 in result_list:
            data["video_id_list"].append(result1)
        for result2 in likeCount_list:
            data["likeCount_list"].append(result2)
        for result3 in commentCount_list:
            data["commentCount_list"].append(result3)

    # make the order random
    combined = list(zip(data["video_id_list"], data["likeCount_list"], data["commentCount_list"]))
    # Shuffle the combined list
    random.shuffle(combined)
    # Unzip the combined list back into individual lists
    data["video_id_list"], data["likeCount_list"], data["commentCount_list"] = zip(*combined)
    # Convert tuples back to lists
    data["video_id_list"] = list(data["video_id_list"])
    data["likeCount_list"] = list(data["likeCount_list"])
    data["commentCount_list"] = list(data["commentCount_list"])

    if data["video_id_list"]:
        for i, video_id in enumerate(data["video_id_list"]):
            video_item = Video.query.filter(Video.vid == video_id).first()
            thumbnail_path = video.get_video_thumbnail_medium(video_item.vid)
            thumbnail_list.append({
                'thumbnail_path': thumbnail_path,
                'video_id': video_item.vid,
                'title': video_item.title,
                'creator': video_item.creator,
                'viewcount': video_item.view_count,
                'likeCount': data["likeCount_list"][i],
                'commentCount': data["commentCount_list"][i]})
        print(thumbnail_list)
        return thumbnail_list
    else:
        return thumbnail_list


def get_week_number(start_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    current_date = datetime.now()
    weeks_since_start = (current_date - start_date).days // 7

    if weeks_since_start % 2 == 0:
        return "week_1"
    else:
        return "week_2"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # publishedAfter = '2023-08-20T00:00:00Z'
        # publishedBefore = '2023-08-27T00:00:00Z'
        # print('new!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # test_get_and_store_video_meta_data('', publishedAfter, publishedBefore)
        # test_get_and_store_video_meta_data('', publishedAfter, publishedBefore)
        # add_new_user('mohan', 'abcdef')
        # test_get_and_store_like_video_meta_data('kpop', publishedAfter, publishedBefore, 'mohan', 10)
        # test_get_and_store_like_video_meta_data('movie', publishedAfter, publishedBefore, 'mohan', 10)
        # test_get_and_store_like_video_meta_data('cooking', publishedAfter, publishedBefore, 'mohan', 10)
        # add_keyword('mohan', 'sunmi')
        # add_keyword('mohan', 'kpop')
        # add_keyword('mohan', 'disney')
        # add_keyword('mohan', 'fruit')
        # add_keyword('mohan', 'movie')
        # add_keyword('mohan', 'car')
        
    # app.run(debug=True)

    app.run(host='0.0.0.0', port=8080)
    # socketio.run(app, host='0.0.0.0', port=8080)