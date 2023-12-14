import whisper

def sample():
    model = whisper.load_model('base')
    result = model.transcribe('D:\Seunghyun\PycharmProjects\Yougle\Yulri-TomatoDiet.m4a')
    print(result['text'])