from googleapiclient.discovery import build
import json
import re
import videos_db_query
import mongo

# api_key = 'AIzaSyAcmY_raQoSUrz6wb-CgZ5fS0FvGweW4pU' # Yooougle
api_key = 'AIzaSyALIZ8k2a6NA5-1t5Evvo3hC1KVgutheN8' # YouglePrac

##################################################################
################### youtube data api를 활용 ########################
##################################################################

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

# DB에 없을 때 channel_id 유튜브의 모든 동영상 목록을 return. json 파일 MongoDB에 저장
def get_channel_videos_and_save(channel_id):
    cid = videos_db_query.get_cid_by_channel_id(channel_id)

    if not cid:
        youtube = build('youtube', 'v3', developerKey=api_key)
        video_info = []
        video_info_mongo = []
        next_page_token = None

        while True:
            res = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
                type='video'
            ).execute()

            for item in res['items']:
                video_info.append({
                    "channel_id": channel_id,
                    "video_id": item['id']['videoId'],
                    "title": item['snippet']['title'],
                    "link": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
                })
            for item in res['items']:
                video_info_mongo.append({
                    # "channel_id": channel_id,
                    "video_id": item['id']['videoId'],
                    "title": item['snippet']['title'],
                    "link": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
                })

            next_page_token = res.get('nextPageToken')
            if not next_page_token:
                break

        cid = videos_db_query.insert_into_channel(channel_id)
        for video in video_info:
            video['cid'] = cid
        videos_db_query.insert_into_video(video_info)

        if not videos_db_query.check_channel_id_in_mongodb(channel_id):
            videos_db_query.save_to_mongodb(channel_id, video_info_mongo)

    return videos_db_query.get_videos_by_cid(cid)
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

