# videos_db_query.py
import sqlite3
import json
import mongo

##################################################################
################### videos.db 를 쿼리합니다. ########################
##################################################################

# Upsert 'video', 'channel' table in MongoDB
def save_to_mongodb(channel_id, video_info_mongo):
    mongo.collection.update_one(
        {"channel_id": channel_id},
        {"$setOnInsert": {"videos": video_info_mongo}},
        upsert=True
    )
    print(f"채널 ID {channel_id}의 정보가 MongoDB에 저장되었습니다.")

# MongoDB에서 채널 정보 가져오기
def get_videos_from_mongodb(channel_id):
    return mongo.collection.find_one({"channel_id": channel_id})

# MongoDB에 채널 ID가 있는지 확인
def check_channel_id_in_mongodb(channel_id):
    return mongo.collection.find_one({"channel_id": channel_id}) is not None

# CREATE 'video', 'channel' table in SQLite videos.db
def create_tables_videosDB():
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        # channel 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel (
                cid INTEGER PRIMARY KEY AUTOINCREMENT, 
                channel_id TEXT
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
                                INSERT INTO video (cid, video_id, title, link)
                                VALUES (?, ?, ?, ?)
                            """, (channel_cid[0], video['video_id'], video['title'], video['link']))
        connect.commit()

# INSERT INTO 'channel' table if not in DB
def insert_into_channel(channel_id):
    with sqlite3.connect('videos.db') as connect:
        cursor = connect.cursor()
        if not cursor.execute("SELECT 1 FROM channel WHERE channel_id = ?", (channel_id,)).fetchone():
            cursor.execute("INSERT INTO channel (channel_id) VALUES (?)", (channel_id,))
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
                SELECT video.vid, video.video_id, video.title, video.link
                FROM video
                INNER JOIN channel ON video.cid = channel.cid
                WHERE channel.cid = ?
            """
            cursor.execute(query, (channel_cid[0],))
            rows = cursor.fetchall()

            video_info = [{"channel_id": row[0],
                   "video_id": row[1],
                   "title": row[2],
                   "link": row[3]} for row in rows]
            print(video_info)
    return [video_info]
    '''
    # JSON 파일에 저장할 비디오 정보 생성
    video_info = [{"channel_id": row[0], "video_id": row[1], "title": row[2], "link": row[3]} for row in rows]

    # 결과를 JSON 파일로 저장
    channel_info = {
        "channel_id": channel_id,
        "videos": video_info
    }
    with open(f'info_{channel_id}.json', 'w', encoding='utf-8') as f:
        json.dump(channel_info, f, indent=4, ensure_ascii=False)
    print(f"채널 ID와 각 동영상의 정보가 'info_{channel_id}.json' 파일로 저장되었습니다.")
    '''

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