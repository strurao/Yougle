import whisper
from whisper.utils import get_writer
import os
import json
def transcribe_audio(mp3_path):
    model = whisper.load_model('medium')
    result = model.transcribe(mp3_path)
    # 각 세그먼트의 텍스트를 줄바꿈하여 출력
    print("dic result", result)
    return result

'''
        for segment in result['segments']:
        print(f"Start: {segment['start']} - End: {segment['end']}")
        print(segment['text'])
        print()
    print(result['text'])  # 텍스트 출력
    print(result['segments'])  # 타임스탬프와 함께 세그먼트 정보 출력
    
    # JSON 파일 경로 설정 (오디오 파일 이름과 동일하되 확장자만 .json으로 변경)
    json_path = os.path.splitext(mp3_path)[0] + ".json"

    # JSON 파일로 저장
    json_writer = get_writer("json", os.path.dirname(json_path))
    json_writer(result, mp3_path)

    # 저장된 JSON 파일 읽기
    with open(json_path, 'r', encoding='utf-8') as file:
        json_result = json.load(file)

    print("HEYYY")
    print(result['text'])

    return json_result
    # print(json.dumps(result['text'], ensure_ascii=False, indent=4))
'''

