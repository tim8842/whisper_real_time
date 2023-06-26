import numpy as np
from multiprocessing import Process, freeze_support
from faster_whisper import WhisperModel
import time
import os
import datetime
import soundfile as sf
from numpy.typing import NDArray
from typing import List, Union, Optional
import random

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
            try:
                self.model = WhisperModel(model_size, device="cuda", compute_type="float16", cpu_threads=12)
            except:
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=12)
        else:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=12)
        self.data: Optional[NDArray] = None
        self.samplerate: Optional[int] = None
        self.noSections: Optional[int] = None
        self.latestText: str = "Телефонный звонок. "
        # self.transcribe_file: str =  transcribe_file

    def __fileWhisperAnalyze(self, path: str, remove: Union[bool, int, None], no_speech_prob: float) -> str:
        """
            Функция отвечает за анализ файла и выдачи теккстового результата
            Аргументы:
              path: Путь до файла (звукового), который нужно обработать
              remove: Удалять ли файл после анализа или нет
              no_speech_prob: Значение вероятности, того, что на участке звуковой дорожке
                нет речи. Если больше этой вероятности, то слова не будут определяться
            Возвращает:
              Строку, результат обработки
        """
        now = datetime.datetime.now()
        # rnd = random.randint(0, 10000)
        filename: str = path
        
        # if os.path.exists(filename):
        segments, _ = self.model.transcribe(filename, language="ru", beam_size=5, best_of=5, patience=0.1, initial_prompt=self.latestText) #max_initial_timestamp=0.5
        text_l: str = ""
        for segment in segments:
            if segment.no_speech_prob > no_speech_prob:
                text_i: str = ""
            else:
                text_i = segment.text
                text_l += text_i
        self.latestText += text_l
        if len(self.latestText) > 2000:
            self.latestText = self.latestText[0:19] + self.latestText[-1500:-1]
            # with open(self.transcribe_file, 'a', encoding='utf-8') as f:
            #     f.write(text_i)
        print(datetime.datetime.now() - now)
        if remove:
            os.remove(filename)
        return text_l

    def analyze(self, path: str = "test.wav", remove:Union[bool, int, None] = False, no_speech_prob: float = 0.8) -> str:
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
            return self.__fileWhisperAnalyze(path, remove, no_speech_prob)
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