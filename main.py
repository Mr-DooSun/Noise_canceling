import matplotlib.pyplot as plt  # 이미지 형태로 오디오의 파형을 그릴수 있게 해주는 라이브러리
import numpy as np  # 수학과 관련된 기능을 고속으로 처리해주는 라이브러리
import scipy.io.wavfile as wave  # WAV 포맷으로 입출력을 할 수 있게 해주는 라이브러리
import speech_recognition as sr  # 음성인식과 관련된 유틸을 포함한 라이브러리
from scipy import signal  # 신호처리와 관련된 유틸을 포함한 라이브러리


# path : wav파일의 위치
# show_plot : 필터링 전/후의 결과를 표시할지의 여부
def filter(path, show_plot=False):
    filename = path[path.rfind('/') + 1:]  # Wav파일의 이름을 구함
    freq, raw_data = wave.read(path)  # Wav를 읽어서 데이터를 구함

    data = []
    if type(raw_data[0]) != np.int16:
        for stereo in raw_data:
            data.append(int(stereo[0]))
    else:
        data = raw_data
    # 1~N개의 채널 중 첫번째 것만 추출함

    b, a = signal.butter(5, 750 / (freq / 2), btype='highpass')
    filtered = signal.lfilter(b, a, data)
    # 750Hz 보다 위의 대역을 소거함

    c, d = signal.butter(5, 450 / (freq / 2), btype='lowpass')
    filtered = signal.lfilter(c, d, filtered)
    # 400Hz 보다 아래의 대역을 소거함

    filtered = np.int16(filtered / np.max(np.abs(filtered)) * 32767)
    # 소리의 크기를 듣기 적절하게 조정함

    if show_plot:  # 필터링/전후 결과 표시가 허용된 경우
        fig, axs = plt.subplots(2, 1)  # 두개의 플롯을 가지는 창을 만듬
        axs[0].plot(data)  # 첫번째 플롯에는 필터링 전의 데이터를 할당함
        axs[1].plot(filtered)  # 두번째 플롯에는 필터링 후의 데이터를 할당함
        plt.show()  # 창을 표시함

    wave.write(f'output/{filename}', freq, filtered)  # Wav 포맷으로 파일을 출력함
    return freq


tmp_filename = 'tmp.wav'  # 버퍼로 사용할 파일이름
r = sr.Recognizer()
i = 0
# 파일이름, 음성인식기를 불러옴

while True:  # KeyboardInterrupt 때 까지 계속 실행
    try:
        with sr.Microphone() as source:  # 마이크로 음성을 불러옴
            print('Wait for speaking')
            audio_data = r.listen(source)  # 오디오 소스중 의미있는 부분인 오디오 데이터를 기록함
            open(tmp_filename, 'wb').write(audio_data.get_wav_data())  # 오디오 소스를 WAV포맷으로 파일시스템에 전송함
            freq = filter(tmp_filename)  # 필터링을 진행함
        with sr.AudioFile(tmp_filename) as source:  # 필터링된 오디오 소스를 불러옴
            audio_data = r.record(source)  # 오디오 소스중 의미있는 부분인 오디오 데이터를 기록함
            text = r.recognize_google(audio_data, language='ko-KR')  # 오디오 데이터를 구글음성인식에 전달하여 평문으로 바꿈

            if "도와" in text:  # 평문에 해당 글자가 포함되면 파일시스템에 전송하고 텍스트를 콘솔에 출력함
                open(f'저장된 호출/{i}.wav', 'wb').write(audio_data.get_wav_data())
                print(f'도움호출 "{text}"')
                i += 1
            else:  # 그렇지 않다면 이상없음과 텍스트을 콘솔에 출력함
                print(f'이상없음 "{text}"')
    except sr.UnknownValueError as e:
        print("* 음성을 인식할수없습니다. *", e)  # 음성인식에 실패하면 콘솔에 출력함