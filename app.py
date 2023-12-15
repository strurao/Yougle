# flask를 구동하고 웹페이지를 라우팅하고 렌더링하여 띄워 줄 python 파일입니다.
from flask import Flask, render_template, request, send_file
import youtube_data, videos_db_query, json
from pytube import YouTube
import mongo
import whisper_sample
import os
from dotenv import load_dotenv
load_dotenv('settings.env')  # 'settings.env' 파일에서 환경 변수 로드

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # CSRF 보호를 위한 비밀 키 설정


@app.route('/download/<channel_id>/<video_id>')
def download_video(channel_id, video_id):
    youtube = YouTube(f'https://www.youtube.com/watch?v={video_id}')
    video = youtube.streams.filter(res='360p', progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not video:
        return "Video not found", 404
    # 현재 스크립트 파일이 위치한 디렉토리의 절대 경로
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # 프로젝트 루트 디렉토리를 찾기 (현재 디렉토리의 상위 디렉토리)
    # project_root = os.path.dirname(current_dir)
    # Yougle 프로젝트 루트 디렉토리 설정
    project_root = 'C:\\Users\\redna\\PycharmProjects\\Yougle'
    # videos 디렉토리 및 채널 ID 디렉토리 경로 설정
    videos_path = os.path.join(project_root, 'videos', channel_id)
    if not os.path.exists(videos_path):
        os.makedirs(videos_path)  # 디렉토리가 없으면 생성
    # 파일명 형식: whisper-channelid-videoid
    filename = f"whisper-{channel_id}-{video_id}.mp4"
    download_path = video.download(output_path=videos_path, filename=filename)
    return send_file(download_path, as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    response_data = {'videos': [], 'channel_id': '', 'error': ''}
    if request.method == 'POST':
        channel_id = request.form['channel_id']
        if not youtube_data.validate_channel_id(channel_id):
            response_data['error'] = 'Invalid Channel ID. Enter again please!'
            return render_template('index.html', data=response_data)
        try:
            response_data['channel_id'] = channel_id

            # bool check values
            exists_in_mongo = videos_db_query.check_channel_id_in_mongodb(channel_id)
            exists_in_sqlite = videos_db_query.check_channel_id_in_sqlite(channel_id)
            # mongo, sqlite 에 없다면 upsert. 목록을 return
            if not exists_in_mongo and exists_in_sqlite:
                youtube_data.update_db(channel_id)

            # mongo 에 있다면 json 데이터 출력하도록
            #if exists_in_mongo:
                #mongo_data = videos_db_query.get_videos_from_mongodb(channel_id)
                #response_data['videos'] = mongo_data['videos'] if mongo_data else []

            # sqlite 에 있다면
            if exists_in_sqlite:
                response_data['videos'] = videos_db_query.innerjoin_by_channel_id(channel_id)

        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            print(e)

    # mongo 에서 가져온 데이터를 JSON 형식으로 변환하여 템플릿에 전달
    #response_data['videos_json'] = json.dumps(response_data['videos'])
    #return render_template('index.html', data=response_data)

    # sqlite 에서 innerjoin한 결과 리스트를 템플릿에 전달
    return render_template('index.html', data=response_data)


if __name__ == '__main__':
    print("0")
    videos_db_query.create_tables_videosDB()
    print("1")
    # whisper_sample.sample()
    # mongo.db.VideoCollection.delete_many({})
    app.run(debug=True)
    print("2")

