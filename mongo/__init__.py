# __init__.py는 Python 모듈이나 패키지가 임포트될 때 자동으로 실행되는 스크립트입니다.
# 여기서 insert_one이 호출되면, 해당 모듈이 어디서든 임포트될 때마다 insert_one이 실행됩니다.
from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017)  # MongoDB의 로컬 인스턴스에 연결
db = client['YougleDB']
collection = db['VideoCollection']

'''
# 'Yooougle'라는 이름의 db로 접속한다. 만약 없으면 자동으로 생성한다.
db = client.VideoSearchAI
# users라는 collection에 doc 딕셔너리 넣기. 다른 이름 사용해도 상관없다! 만약 collection이 없다면 생성됨.
# Collection은 비슷한 것들끼리 모아둔 테이블. Collection 안의 데이터 한 줄을 Document.
doc = {'name':'whyyy', 'age':23}
# db.users.insert_one(doc)

same_ages = list(db.users.find({'age':23},{'_id':False}))
print(same_ages)

# MongoDB 데이터베이스 내의 모든 컬렉션 이름 조회
collection_names = db.list_collection_names()
print("collection_names")
print(collection_names)

# MongoDB 인스턴스의 모든 데이터베이스 이름 조회
database_names = client.list_database_names()
print("db_names")
print(database_names)


# 전체 컬렉션 삭제
#db.drop_collection('users')

# MongoDB 데이터베이스 내의 모든 컬렉션 이름 조회
collection_names = db.list_collection_names()
print("collection_names")
print(collection_names)

# MongoDB 인스턴스의 모든 데이터베이스 이름 조회
database_names = client.list_database_names()
print("db_namse")
print(database_names)

all_documents = db.users.find()
if all_documents.count() == 0:
    print("None")

# 조회된 문서 출력
for document in all_documents:
    print(document)
'''