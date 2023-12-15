# flask를 구동하고 웹페이지를 라우팅하고 렌더링하여 띄워 줄 python 파일입니다.
from flask import Flask, render_template, request
import youtube_data, videos_db_query, json
import mongo
import whisper_sample
import os
from dotenv import load_dotenv
load_dotenv('settings.env')  # 'settings.env' 파일에서 환경 변수 로드

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # CSRF 보호를 위한 비밀 키 설정

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
            exists_in_mongo = videos_db_query.check_channel_id_in_tables(channel_id)
            if not exists_in_mongo:
                youtube_data.get_channel_videos_and_save(channel_id)
            mongo_data = videos_db_query.get_videos_from_mongodb(channel_id)
            response_data['videos'] = mongo_data['videos'] if mongo_data else []
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            print(e)

    # MongoDB에서 가져온 데이터를 JSON 형식으로 변환하여 템플릿에 전달
    response_data['videos_json'] = json.dumps(response_data['videos'])
    return render_template('index.html', data=response_data)
    #return render_template('index.html', videos=videos_list_result, channel_id=channel_id)

if __name__ == '__main__':
    print("0")
    videos_db_query.create_tables_videosDB()
    print("1")
    # whisper_sample.sample()
    # mongo.db.VideoCollection.delete_many({})
    app.run(debug=True)
    print("2")

