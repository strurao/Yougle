# db 를 쿼리합니다.
import sqlite3
import json
import mongo

# Upsert 'video', 'channel' table in MongoDB
def save_to_mongodb(channel_id, video_info_mongo):
    mongo.collection.update_one(
        {"channel_id": channel_id},
        {"$setOnInsert": {"videos": video_info_mongo}},
        upsert=True
    )
    print(f"채널 ID {channel_id}의 정보가 MongoDB에 저장되었습니다.")

def check_transcription_none(channel_id, video_id):
    # MongoDB 쿼리 실행
    result = mongo.collection.find_one(
        {"channel_id": channel_id, "videos.video_id": video_id},
        {"videos.$": 1}
    )
    # 결과 확인 및 반환
    if result is not None and 'videos' in result:
        video_info = result['videos'][0]
        return video_info.get('transcription') is None # null 이면 return True
    else:
        return None  # 채널 ID 또는 비디오 ID가 잘못되었거나 결과가 없는 경우

def upsert_mongodb_trans(channel_id, video_id, transcription):
    # MongoDB에 upsert 작업 수행
    mongo.collection.update_one(
        {"channel_id": channel_id, "videos.video_id": video_id},  # 찾을 문서의 조건
        {"$set": {"videos.$.transcription": transcription}},  # 업데이트할 내용
        upsert=True  # 해당하는 문서가 없으면 새로운 문서를 삽입
    )
    print("upsert_mongodb_trans: ", transcription)

def find_mongodb_trans(channel_id, video_id):
    # MongoDB 에서 자막 정보 찾기
    result = mongo.collection.find_one(
        {"channel_id": channel_id, "videos.video_id": video_id},
        {"videos.$": 1}  # videos 배열에서 해당 비디오 ID의 문서만 반환
    )
    # 결과에서 transcription 값 추출 및 반환
    if result is not None and 'videos' in result and len(result['videos']) > 0:
        return result['videos'][0].get('transcription')
    else:
        return None  # 해당하는 transcription 정보가 없는 경우

# MongoDB에서 채널 정보 가져오기
def get_videos_from_mongodb(channel_id):
    return mongo.collection.find_one({"channel_id": channel_id})

# MongoDB에 채널 ID가 있는지 확인
def check_channel_id_in_mongodb(channel_id):
    return mongo.collection.find_one({"channel_id": channel_id}) is not None

def check_channel_id_in_sqlite(channel_id):
    # SQLite 데이터베이스에 연결
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        # 채널 ID 조회
        cursor.execute("SELECT EXISTS(SELECT 1 FROM channel WHERE channel_id = ?)", (channel_id,))
        exists = cursor.fetchone()[0]
        return exists == 1

def check_channel_id_in_both_db(channel_id):
    # MongoDB에서 확인
    in_mongodb = check_channel_id_in_mongodb(channel_id)
    # SQLite에서 확인
    in_sqlite = check_channel_id_in_sqlite(channel_id)
    return in_mongodb and in_sqlite

# CREATE 'video', 'channel' table in SQLite videos.db
def create_tables_videosDB():
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        # channel 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel (
                cid INTEGER PRIMARY KEY AUTOINCREMENT, 
                channel_id TEXT,
                channel_name TEXT
            )
        """)
        connect.commit()

        # video 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video (
                vid INTEGER PRIMARY KEY AUTOINCREMENT,
                cid INTEGER,
                video_id TEXT,
                title TEXT,
                link TEXT,
                published_at TEXT,
                FOREIGN KEY (cid) REFERENCES channel(cid)
            )
        """)
        connect.commit()

# INSERT INTO 'video' table if not in SQLite videos.db
def insert_into_video(videos_list):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()

        for video in videos_list:
            # channel_id를 cid로 변환
            cursor.execute("SELECT cid FROM channel WHERE channel_id = ?", (video['channel_id'],))
            channel_cid = cursor.fetchone()

            if channel_cid:
                # 이미 존재하는 video_id 확인
                cursor.execute("SELECT 1 FROM video WHERE video_id = ?", (video['video_id'],))
                if not cursor.fetchone():
                    # 중복되지 않은 경우, 새로운 레코드 삽입
                    cursor.execute("""
                                INSERT INTO video (cid, video_id, title, link, published_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (channel_cid[0], video['video_id'], video['title'], video['link'], video['published_at']))
        connect.commit()

# INSERT INTO 'channel' table if not in DB
def insert_into_channel(channel_id, channel_name):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        if not cursor.execute("SELECT 1 FROM channel WHERE channel_id = ?", (channel_id,)).fetchone():
            cursor.execute("INSERT INTO channel (channel_id, channel_name) VALUES (?, ?)", (channel_id, channel_name))
        connect.commit()
        return cursor.lastrowid  # 새로 삽입된 채널의 cid 반환


# 사용자로부터 입력받은 channel_id로, video 테이블과 channel 테이블 존재 여부 확인
def check_channel_id_in_tables(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM channel WHERE channel_id=?)", (channel_id,))
        return cursor.fetchone()[0] == 1

# 사용자로부터 입력받은 channel_id로, video 테이블과 channel 테이블 JOIN
def innerjoin_by_channel_id(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT cid FROM channel WHERE channel_id = ?", (channel_id,))
        channel_cid = cursor.fetchone()
        if channel_cid:
            query = """
                SELECT video.vid, video.video_id, video.title, video.link, video.published_at
                FROM video
                INNER JOIN channel ON video.cid = channel.cid
                WHERE channel.cid = ?
                ORDER BY video.published_at DESC
            """
            cursor.execute(query, (channel_cid[0],))
            rows = cursor.fetchall()

            video_info = [{"vid": row[0],
                "video_id": row[1],
                "title": row[2],
                "link": row[3],
                "published_at": row[4]} for row in rows]
            print(video_info)
    return video_info

def get_cid_by_channel_id(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT cid FROM channel WHERE channel_id = ?", (channel_id,))
        result = cursor.fetchone()
    return result[0] if result else None

def get_videos_by_cid(cid):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT link FROM video WHERE cid = ?", (cid,))
        videos = [row[0] for row in cursor.fetchall()]
    return videos

# sqlite 에서 특정 채널에 속하는 영상의 개수를 알아내기
def get_video_count(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM video
            INNER JOIN channel ON video.cid = channel.cid
            WHERE channel.channel_id = ?
        """, (channel_id,))
        count = cursor.fetchone()[0]
        return count

# sqlite 에서 특정 채널의 이름 알아내기
def get_channel_name(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT channel_name FROM channel WHERE channel_id = ?", (channel_id,))
        result = cursor.fetchone()
        return result[0] if result else None

##################################################################
######################### not using ##############################
##################################################################

# 확장성 개선을 위한 제안적인 코드
def execute_query(query, params=()):
    """데이터베이스 쿼리 실행 및 결과 반환 함수"""
    with sqlite3.connect('videos.db') as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def fetch_column_data(table, column):
    """지정된 테이블의 특정 열 데이터를 가져오는 함수"""
    query = f"SELECT {column} FROM {table}"
    try:
        return [row[0] for row in execute_query(query)]
    except sqlite3.DatabaseError as e:
        print(f"데이터베이스 오류: {e}")
        return []

# JOIN 'video', 'channel' table
    # PRIMARY KEY 인 channel_id 를 기준으로, video 테이블과 channel 테이블을 JOIN.
    # JOIN 예시를 위한 함수입니다.
def join_channel_id():
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""
                    SELECT video.channel_id, channel.channel_id
                    FROM video
                    INNER JOIN channel ON video.channel_id = channel.channel_id
                """)
        results = cursor.fetchall()
        return len(results) > 0  # 결과가 있으면 True, 없으면 False 반환

# INSERT INTO 'video' table manually for test
def insert_into_video_manually(videos_list):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        for v in videos_list:
            if not cursor.execute("SELECT 1 FROM video WHERE video_id = ?", (v[1],)).fetchone():
                cursor.execute("INSERT INTO video (channel_id, video_id, title, link) VALUES (?, ?, ?, ?)", v)
        connect.commit()

# INSERT INTO 'channel' table manually for test
def insert_into_channel_manually(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        if not cursor.execute("SELECT 1 FROM channel WHERE channel_id = ?", (channel_id,)).fetchone():
            cursor.execute("INSERT INTO channel (channel_id) VALUES (?)", (channel_id,))
        connect.commit()