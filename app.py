# -*- coding: utf-8 -*-

# flask를 구동하고 웹페이지를 라우팅하고 렌더링하여 띄워 줄 python 파일입니다.
import ssl
import sys
from flask import Flask, render_template, request, send_file, jsonify
import youtube_data, videos_db_query, mongo, json
from pytube import YouTube
import whisper_trans
import os
import openai
from dotenv import load_dotenv
load_dotenv('settings.env')  # 'settings.env' 파일에서 환경 변수 로드

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # CSRF 보호를 위한 비밀 키 설정
openai.api_key = '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'


# 타임스탬프, 자막텍스트 보기
@app.route('/view-time-transcription/<channel_id>/<video_id>')
def view_time_transcription(channel_id, video_id):
    transcription = videos_db_query.find_mongodb_trans(channel_id, video_id)
    if transcription is None:
        return "Transcription not found", 404

    # 각 segment 의 시간을 분:초 형식으로 변환한다.
    for segment in transcription['segments']:
        segment['formatted_start'] = youtube_data.format_seconds_to_min_sec(segment['start'])
    return render_template('transcription.html', transcription=transcription, video_id=video_id)

# 자막텍스트 통합 보기
@app.route('/view-entire-transcription/<channel_id>/<video_id>')
def view_entire_transcription(channel_id, video_id):
    transcription = videos_db_query.find_mongodb_trans(channel_id, video_id)
    if transcription is None:
        return "Transcription not found", 404

    # 전체 스크립트를 하나의 문자열로 결합
    entire_transcription = " ".join(segment['text'] for segment in transcription['segments'])
    transcription_data = {
        'video_id': video_id,
        'script': entire_transcription
    }
    return render_template('entire_transcription.html', transcription=transcription_data)

# mongodb에 자막 정보 저장하기
@app.route('/download/<channel_id>/<video_id>')
def download_video(channel_id, video_id):
    print("0000")
    youtube = YouTube(f'https://www.youtube.com/watch?v={video_id}')
    # youtube = YouTube('https://www.youtube.com/watch?v=' + video_id)
    video = youtube.streams.filter(res='360p', progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not video:
        return "Video not found", 404

    project_root = 'C:\\Users\\redna\\PycharmProjects\\Yougle'
    videos_path = os.path.join(project_root, 'videos', channel_id)
    if not os.path.exists(videos_path):
        os.makedirs(videos_path)
    filename = f"whisper-{channel_id}-{video_id}.mp4"
    mp4_path = os.path.join(videos_path, filename)
    mp3_path = os.path.join(videos_path, f"whisper-{channel_id}-{video_id}.mp3")
    video.download(output_path=videos_path, filename=filename)
    youtube_data.convert_mp4_to_mp3(mp4_path, mp3_path)

    # whisper, transcription
    not_exist_json_in_mongo = videos_db_query.check_transcription_none(channel_id, video_id)

    if not_exist_json_in_mongo: # 없으면 저장
        transcription = whisper_trans.transcribe_audio(mp3_path)
        print("transcription", transcription)
        videos_db_query.upsert_mongodb_trans(channel_id, video_id, transcription)
        print("app.py : upserted transcription in mongodb", channel_id, video_id, transcription)

        # 여기서부터 텍스트 파일 저장 로직 추가
        transcripts_path = os.path.join('C:\\Users\\redna\\PycharmProjects\\Yougle', 'transcripts', channel_id)
        if not os.path.exists(transcripts_path):
            os.makedirs(transcripts_path)
        transcript_file_path = os.path.join(transcripts_path, f"{video_id}_transcript.txt")

        with open(transcript_file_path, 'w', encoding='utf-8') as file:
            file.write(f"video_id: {video_id}\n\nscript: ")
            file.write(" ".join(segment['text'] for segment in transcription['segments']) + '\n')

    if not not_exist_json_in_mongo: # 있으면 꺼내오기
        transcription = videos_db_query.find_mongodb_trans(channel_id, video_id)
        print("app.py : transcription already exists in mongo")

    return send_file(mp3_path, as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    response_data = {'videos': [], 'channel_id': '', 'error': '',
                     'video_cnt': 0, 'published_at': '', 'channel_name': '',
                     'channel_link': '', 'total_pages': 0, 'current_page': 1} # 기본값으로 current_page를 1로 설정

    # GET 요청에서 채널 ID 가져오기
    channel_id = request.args.get('channel_id', '')

    if request.method == 'POST':
        channel_id = request.form['channel_id']
        if not youtube_data.validate_channel_id(channel_id):
            response_data['error'] = 'Invalid Channel ID. Enter again please!'
            return render_template('index.html', data=response_data)

        #if youtube_data.validate_channel_id(channel_id):
            #print("validate!!!")
        try:
            response_data['channel_id'] = channel_id
            # bool check values
            exists_in_mongo = videos_db_query.check_channel_id_in_mongodb(channel_id)
            exists_in_sqlite = videos_db_query.check_channel_id_in_sqlite(channel_id)
            # mongo, sqlite 에 없다면 upsert. 목록을 return
            if not exists_in_mongo and not exists_in_sqlite:
            # if not exists_in_sqlite:
                youtube_data.update_db(channel_id)
                print("!!! not in dbs")
            # mongo 에 있다면 json 데이터 출력하도록
            #if exists_in_mongo:
                #mongo_data = videos_db_query.get_videos_from_mongodb(channel_id)
                #response_data['videos'] = mongo_data['videos'] if mongo_data else []
            # sqlite 에 있다면
            elif exists_in_sqlite:
                print("!!! in sqlite")
            '''
            response_data['videos'] = videos_db_query.innerjoin_by_channel_id(channel_id)
            response_data['video_cnt'] = videos_db_query.get_video_count(channel_id)
            response_data['channel_name'] = videos_db_query.get_channel_name(channel_id)
            response_data['channel_link'] = videos_db_query.get_channel_link(channel_id)
            '''
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            # print(e)
            return render_template('index.html', data=response_data)

    # 페이지네이션 처리는 POST와 무관하게 수행
    page = request.args.get('page', 1, type=int) # 페이지 번호 # HTTP GET
    per_page = 20  # 한 페이지당 비디오 수
    if channel_id:
        response_data['channel_id'] = channel_id
        total_videos = videos_db_query.get_video_count(channel_id)
        total_pages = (total_videos + per_page - 1) // per_page # 총 페이지 수는 전체 동영상 수를 페이지당 동영상 수로 나누어 계산
        # 현재 페이지에 대한 정보와 함께, 채널 이름과 링크도 함께 업데이트하여 response_data에 저장
        response_data['videos'] = videos_db_query.get_videos_by_page(channel_id, page, per_page)
        response_data['video_cnt'] = videos_db_query.get_video_count(channel_id)
        response_data['total_pages'] = total_pages
        response_data['current_page'] = page
        channel_name = videos_db_query.get_channel_name(channel_id)
        if channel_name:
            response_data['channel_name'] = channel_name  # 채널 이름 설정
            response_data['channel_link'] = videos_db_query.get_channel_link(channel_id)

        print("!!! pagination")

    return render_template('index.html', data=response_data)
    # mongo 에서 가져온 데이터를 JSON 형식으로 변환하여 템플릿에 전달
    #response_data['videos_json'] = json.dumps(response_data['videos'])
    #return render_template('index.html', data=response_data)
    # sqlite 에서 innerjoin한 결과 리스트를 템플릿에 전달


@app.route('/gpt-query', methods=['GET'])
def gpt_query():
    user_prompt = request.args.get('query')
    channel_id = request.args.get('channel_id')

    try:
        # 데이터베이스에서 채널의 자막 정보를 가져옵니다.
        transcriptions = videos_db_query.find_all_transcriptions_for_channel(channel_id)
        if not transcriptions:
            return jsonify({'error': 'No transcriptions found for the channel'}), 404

        combined_transcription = " ".join(t['text'] for t in transcriptions)

        try:
            # OpenAI Assistant API와 상호작용합니다.
            response = openai.ChatCompletion.create(
                model="gpt-4 turbo",
                messages=[
                    {"role": "system", "content": "This is a helpful assistant."},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": combined_transcription}
                ]
            )

            return jsonify({
                'gpt_response': response.choices[0].message.content,
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': 'Database query failed: ' + str(e)}), 500


if __name__ == '__main__':
    print("현재 작업 디렉토리:", os.getcwd())
    videos_db_query.create_tables_videosDB()
    # mongo.db.VideoCollection.delete_many({})
    app.run(host='203.152.178.190', port=5000, debug=True)
    # app.run(host='0.0.0.0', port=8080, debug=True)

    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # ssl_context.load_cert_chain(certfile='newcert.pem', keyfile='newkey.pem', password='secret')
    # app.run(host='203.152.178.190', port=5000, debug=True, ssl_context=ssl_context)
