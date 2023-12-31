import numpy as np
from faster_whisper import WhisperModel
import os
import datetime
import soundfile as sf
from numpy.typing import NDArray
from typing import List, Union, Optional

class WhisperAnalysier():
    """
        Класс WhisperAnalusier предназначен для анализа звуковых 
        дорожек.
    """
    def __init__(self, model_size: str = "base", model_type: str = "cuda") -> None: # transcribe_file: str = "transcript.txt"
        """
            Инициализация
            Аргументы:
              model_size: размер модели, в зависимости от нее модель лучше или хуже распознает слова
                также влияет на скорость выполнения (tiny, tiny.en, base, base.en,
                small, small.en, medium, medium.en, large-v1, or large-v2)
              model_type: устройство на чем будет работать анализ отрывков.
                cuda - видеокарта, cpu - процессор
        """
        if model_type == "cuda":
     
            self.model = WhisperModel(model_size, device="cuda", compute_type="float16", cpu_threads=6)
       

        self.data: Optional[NDArray] = None
        self.samplerate: Optional[int] = None
        self.noSections: Optional[int] = None
        # self.transcribe_file: str =  transcribe_file

    def __fileWhisperAnalyze(self, path: str, remove: Union[bool, int, None]) -> str:
        """
            Функция отвечает за анализ файла и выдачи теккстового результата
            Аргументы:
              path: Путь до файла (звукового), который нужно обработать
              remove: Удалять ли файл после анализа или нет
            Возвращает:
              Строку, результат обработки
        """
        now = datetime.datetime.now()
        # rnd = random.randint(0, 10000)
        filename: str = path
        
        # if os.path.exists(filename):
        audioLenghtS = len(self.data) / self.samplerate
        ms = audioLenghtS * 1000 - 200
        segments, _ = self.model.transcribe(filename, language="ru" , vad_filter=True, vad_parameters=dict(min_silence_duration_ms=ms), word_timestamps=True, beam_size=5, best_of=5, condition_on_previous_text=False) #max_initial_timestamp=0.5
        text_l: str = ""
        for segment in segments:
            text_i: str = segment.text
            text_l += text_i
        print(datetime.datetime.now() - now)
        if remove:
            os.remove(filename)
        return text_l

    def analyze(self, path: str = "test.wav", remove:Union[bool, int, None] = False) -> str:
        """
            Функция отвечает за считывание параметров звукового файла
            и применение функции анализа
            Аргументы:
              path: Путь до файла (звукового), который нужно проанализировать
              remove: Удалять ли файл после анализа или нет
            Возвращает:
              Строку, результат обработки
        """
        # with open(self.transcribe_file, 'w', encoding='utf-8') as f:
        #     pass
        self.data, self.samplerate = sf.read(path)
        self.noSections = int(np.ceil(len(self.data) / self.samplerate))
        try:
            return self.__fileWhisperAnalyze(path, remove)
        except FileNotFoundError as e:
            return "error"
 

def startWaProcess():
    wa = WhisperAnalysier(model_size="large-v2", model_type="cuda")
    wa.analyzeWithThread(path="14302023113031707A.wav")
    wa.analyzeWithThread(path="14302023113031707A.wav")
    wa.analyzeWithThread(path="14302023113031707A.wav")
    wa.analyzeWithThread(path="14302023113031707A.wav")



if __name__ == "__main__":
    startWaProcess()