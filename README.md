# Project Yougle
### 📌 프로젝트 소개

>_**"영상 속 내용을 이해하는 것보다, 제대로 된 영상을 찾는 것이 어렵다!"**_ 🧐

정보가 넘쳐나는 시대이며, 많은 사람들이 유튜브로 검색하는 시대입니다. 하지만 정보의 양이 늘어난 만큼 원하는 정보를 찾기 어려워졌습니다. 그래서 임의의 채널에서 사용자가 원하는 정보를 쉽게 검색할 수 있는 유튜브 검색 GPTs 서비스를 제작하고 있습니다. 

Linux 클라우드 서버에서 Flask,  mongoDB, SQLite, 그리고 GPT API를 사용하여 관리자 페이지를 구현했습니다. 
대량의 자막 JSON 정보를 저장하고 빠르게 조회하기 위해 mongoDB를, 그리고 유튜브 채널 정보를 저장하기 위해 SQLite를 사용해 CRUD기능을 처리했습니다. 현재는 작업의 자동화를 위한 REFTful API를 기반으로 작업하고 있습니다.

---

### 📌 담당한 기능
- Schema 설계, 데이터 저장
- Youtube 정보 처리 
- Whisper 이용한 Subtitle 데이터 처리 
- 관리자 페이지 구성
  - 관리자 페이지 (수동 버전) 실행 영상 보기 : https://youtu.be/u--PyyFtTIQ
- GPTs Action Schema, API 설계
- 현재 데이터 저장 자동화 기능을 구현 중에 있습니다.

---

### 📌 사용한 skill
- Linux (Ubuntu)
- vim
- Python3.9 & Pycharm (Window, MacOS)
- Javascript, HTML, CSS
- SQLite, MongoDB
- [Google YouTube Data API](https://developers.google.com/youtube/v3)
- [OpenAI Whisper](https://github.com/openai/whisper)

---

### 📌 개발일지 블로그
https://velog.io/@strurao/series/Yougle 

---
### 📌 Linux Cloud 실행 화면
![image](https://github.com/strurao/Yougle/assets/126440235/56535241-cceb-40f1-83b2-16dc7a743e53)

### 📌 관리자 페이지 구성
![image](https://github.com/strurao/Yougle/assets/126440235/6c1676e1-32cd-448e-92a5-64c62d8bb52e)
