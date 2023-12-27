# youtube data api를 활용합니다.
from googleapiclient.discovery import build
import json
import re
import videos_db_query
import html  # HTML 엔티티를 처리하기 위한 모듈 추가
from moviepy.editor import VideoFileClip
import mongo
import os

# api_key = 'AIzaSyAcmY_raQoSUrz6wb-CgZ5fS0FvGweW4pU' # Yooougle
# api_key = 'AIzaSyALIZ8k2a6NA5-1t5Evvo3hC1KVgutheN8' # YouglePrac
api_key = 'AIzaSyCKrtb3S0YXnbXsoh1zKLv3dieVeii_uwg' # YouglePractice

# 자막 정보의 타임스탬프를 [초] 형식에서 [분:초] 형식으로 변환합니다.
def format_seconds_to_min_sec(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# mp4->mp3 변환
def convert_mp4_to_mp3(mp4_file_path, mp3_file_path):
    video_clip = VideoFileClip(mp4_file_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(mp3_file_path)
    audio_clip.close()
    video_clip.close()

# YouTube 채널 ID가 유효한지 검증하는 함수
def validate_channel_id(channel_id):
    if not channel_id:
        return False
    if not channel_id.startswith('UC'):
        return False
    if not len(channel_id) == 24:
        return False
    if not re.match('^[a-zA-Z0-9_-]+$', channel_id):
        return False
    return True

# DB에 없을 때 sqlite, mongodb 각각에 저장
def update_db(channel_id):
    cid = videos_db_query.get_cid_by_channel_id(channel_id)

    if not cid:
        youtube = build('youtube', 'v3', developerKey=api_key)
        video_info = [] # sqlite
        video_info_mongo = [] # mongodb
        next_page_token = None

        # 유튜브 채널 정보를 가져와 채널 이름을 추출합니다.
        channel_response = youtube.channels().list(
            part='snippet',
            id=channel_id
        ).execute()
        channel_name = channel_response['items'][0]['snippet']['title'] if channel_response['items'] else 'Unknown'

        while True:
            res = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
                type='video',
                order = 'date'  # 결과를 최신 순으로 정렬
            ).execute()

            for item in res['items']:
                title = html.unescape(item['snippet']['title'])  # HTML 엔티티를 일반 텍스트로 변환
                video_info.append({ # sqlite
                    "channel_id": channel_id,
                    "video_id": item['id']['videoId'],
                    "title": title,
                    "link": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}',
                    "published_at": item['snippet']['publishedAt']  # 업로드 날짜 추가
                })

            for item in res['items']:
                title = html.unescape(item['snippet']['title'])  # HTML 엔티티를 일반 텍스트로 변환
                video_info_mongo.append({ # mongodb
                    # "channel_id": channel_id,
                    "video_id": item['id']['videoId'],
                    "title": title,
                    "link": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}',
                    "transcription": None, # JSON
                    "published_at": item['snippet']['publishedAt']  # 업로드 날짜 추가
                })

            next_page_token = res.get('nextPageToken')
            if not next_page_token:
                break

        cid = videos_db_query.insert_into_channel(channel_id, channel_name)
        for video in video_info:
            video['cid'] = cid
        videos_db_query.insert_into_video(video_info) # sqlite

        videos_db_query.save_to_mongodb(channel_id, video_info_mongo)  # mongodb

        #if not videos_db_query.check_channel_id_in_mongodb(channel_id):
            #videos_db_query.save_to_mongodb(channel_id, video_info_mongo) # mongodb
    # return videos_db_query.get_videos_by_cid(cid)

    '''
    # 결과를 JSON 파일로 저장
    channel_info = {
        "channel_id": channel_id,
        "videos": video_info
    }
    with open(f'info_{channel_id}.json', 'w', encoding='utf-8') as f:
        json.dump(channel_info, f, indent=4, ensure_ascii=False)
    print(f"채널 ID와 각 동영상의 정보가 'info_{channel_id}.json' 파일로 저장되었습니다.")
    '''


##################################################################
######################### not using ##############################
##################################################################

# prototype
def get_channel_id(url):
    # 유튜브 채널 URL에서 'UC'로 시작하는 채널 ID를 추출하는 정규 표현식
    pattern = r'youtube\.com\/channel\/(UC[-_A-Za-z0-9]{21}[AQgw])'
    match = re.search(pattern, url)

    if match:
        # 정규 표현식에 해당하는 부분을 찾으면, 그 부분을 반환
        return match.group(1)
    else:
        # 채널 ID를 찾지 못하면 None 반환
        return None

def get_video_links(api_key, channel_url):
    youtube = build('youtube', 'v3', developerKey=api_key)
    channel_id = get_channel_id(channel_url)

    video_links = []
    request = youtube.search().list(part='snippet', channelId=channel_id, maxResults=50, type='video')
    response = request.execute()

    for item in response['items']:
        video_id = item['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append({"title": item['snippet']['title'], "link": video_link})

    # 결과를 JSON 파일로 저장
    with open('video_links.json', 'w', encoding='utf-8') as f:
        json.dump(video_links, f, indent=4, ensure_ascii=False)
    print("동영상 목록이 'video_links.json' 파일에 저장되었습니다.")

#if __name__ == '__main__':
def get_links_of_id():
    api_key = 'AIzaSyAcmY_raQoSUrz6wb-CgZ5fS0FvGweW4pU'  # API 키
    channel_url = input("YouTube 채널 URL을 입력하세요: ")
    get_video_links(api_key, channel_url)

