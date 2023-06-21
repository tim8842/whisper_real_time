import numpy as np
import soundfile as sf
from multiprocessing import Process, freeze_support
from faster_whisper import WhisperModel
from threading import Thread
import time
import os
from copy import copy
import keyboard
import sys
from typing import List
from MicrophoneGenerator import MicrophoneGenerator
import shutil
import datetime

class WhisperAnalysier():
    def __init__(self, model_size = "base", model_type="cuda", transcribe_file="transcript.txt") -> None:
        if model_type == "cuda":
            try:
                self.model = WhisperModel(model_size, device="cuda", compute_type="float16")
            except:
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        else:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.data = None
        self.samplerate = None
        self.noSections = None
        self.flThreadIsWork = False
        self.fwThreadIsWork = False
        self.micGen = None
        self.input_type = None
        self.transcribe_file =  transcribe_file
        # self.segments = []
        self.writeInTxtIsWork = False


    def __createTmpSoundFile(self, prefix:float, duration:float) -> str:
        temp = self.data[int(prefix*self.samplerate):int(prefix*self.samplerate+self.samplerate*duration)]
        filename = f"sounds/test{prefix}.wav"
        sf.write(filename, temp, self.samplerate)
        return filename

    # def __writeInTxt(self, index):
    #     while self.writeInTxtIsWork:
    #         if self.segments and len(self.segments) > index:
    #             segments = self.segments.pop(index)
    #             for segment in segments:
    #                 with open(self.transcribe_file, 'a', encoding='utf-8') as f:
    #                     f.write(segment.text)


    def __fileWhisperAnalyze(self, prefix:float):
        filename = f"sounds/test{prefix}.wav"
        # now = datetime.datetime.now()
        segments, _ = self.model.transcribe(filename, language="ru")
        # self.segments.append(segments)
        for segment in segments:
            with open(self.transcribe_file, 'a', encoding='utf-8') as f:
                if segment.no_speech_prob > 0.78:
                    text_i = ""
                else:
                    text_i = segment.text
                f.write(text_i)
        #     print("[%.2fs -> %.2fs] %s при prefix = %f" % (segment.start, segment.end, segment.text, prefix))
        # print(datetime.datetime.now() - now)
        os.remove(filename)

    def analyzeWithoutThread(self, input_type = "file", duration = 3, step = 1.5, name = "test.wav") -> None:
        self.input_type = input_type
        with open(self.transcribe_file, 'w', encoding='utf-8') as f:
            pass
        self.__deleteAndCreateCatalog()
        if input_type == "file":
            self.data, self.samplerate = sf.read(name)
            self.noSections = int(np.ceil(len(self.data) / self.samplerate))
            self.__analyzeFileStreamWithoutThread(duration, step)
        elif input_type == "microphone":
            self.micGen = self.__createMicrophoneInstance()
            self.micGen.start_stream()
            self.__analyzeMicrophoneStreamWithoutThread(duration, step)
            self.micGen.stop_stream()
        else:
            raise SystemExit(f"error in input_type, it can't be {input_type}, mb 'file' or 'microphone'")

    # def __analyzeMicrophoneAsync(self, duration, step):
    #     try:
    #         self.micGen.record(duration, step)
    #         fw = Thread(target=self.__fileWhisperStreamThread, args=(step,))
    #         # w = Thread(target=self.__writeInTxt, args=(0,))
    #         # w.daemon = True
    #         fw.daemon = True
    #         self.fwThreadIsWork = True
    #         fw.start()
    #         # self.writeInTxtIsWork = True
    #         # w.start()
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         print("thread ended")

    # def analyzeAsync(self, input_type = "file", duration = 3, step = 1.5, name = "test.wav") -> None:
    #     self.input_type = input_type
    #     self.__deleteAndCreateCatalog()
    #     if input_type == "file":
    #         self.data, self.samplerate = sf.read(name)
    #         self.noSections = int(np.ceil(len(self.data) / self.samplerate))
    #         self.__analyzeFileStreamWithoutThread(duration, step)
    #     elif input_type == "microphone":
    #         self.micGen = self.__createMicrophoneInstance()
    #         self.micGen.start_stream()
    #         self.__analyzeMicrophoneStreamWithoutThread(duration, step)
    #         self.micGen.stop_stream()
    #     else:
    #         raise SystemExit(f"error in input_type, it can't be {input_type}, mb 'file' or 'microphone'")

    def __deleteAndCreateCatalog(self, path = "sounds"):
        try:
            shutil.rmtree(path) 
        except:
            print(f"каталога {path} не существует")
        try:
            os.mkdir(path)
        except:
            print(f"Каталог {path} не может создаться")

    def __analyzeMicrophoneStreamWithoutThread(self, duration:float, step:float) -> None:
        prefix = 0
        while True:
            self.micGen.recordOneTime(duration, step)
            self.__fileWhisperAnalyze(prefix)
            prefix = (prefix + step) % self.noSections

    def __createMicrophoneInstance(self) -> MicrophoneGenerator:
        micGen = MicrophoneGenerator()
        self.noSections = micGen.prefixDevider
        return micGen

    def analyzeWithThread(self, input_type = "file", duration = 3, step = 1.5, name = "test.wav") -> None:
        self.input_type = input_type
        self.__deleteAndCreateCatalog()
        with open(self.transcribe_file, 'w', encoding='utf-8') as f:
            pass
        if input_type == "file":
            self.data, self.samplerate = sf.read(name)
            self.noSections = int(np.ceil(len(self.data) / self.samplerate))
            self.__analyzeFileStreamWithThread(duration, step)
        elif input_type == "microphone":
            self.micGen = self.__createMicrophoneInstance()
            self.micGen.start_stream()
            self.__analyzeMicrophoneStreamWithThread(duration, step)

    def __fileListenerStreamThread(self, duration:float, step:float) -> None:
        prefix = 0
        while (prefix < self.noSections):
            self.__createTmpSoundFile(prefix, duration)
            time.sleep(step)
            prefix += step
        self.flThreadIsWork = False


    def __fileWhisperStreamThread(self, step:float) -> None:
        prefix = 0
        while (prefix < self.noSections):
            try:
                self.__fileWhisperAnalyze(prefix)
                if self.input_type == "file":
                    prefix += step
                else:
                    prefix = (prefix + step) % self.noSections
            except FileNotFoundError as e:
                pass
        self.fwThreadIsWork = False

    def __analyzeMicrophoneStreamWithThread(self, duration:float, step:float) -> None:
        try:
            self.micGen.record(duration, step)
            fw = Thread(target=self.__fileWhisperStreamThread, args=(step,))
            # w = Thread(target=self.__writeInTxt, args=(0,))
            # w.daemon = True
            fw.daemon = True
            self.fwThreadIsWork = True
            fw.start()
            # self.writeInTxtIsWork = True
            # w.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("thread ended")

    def __analyzeFileStreamWithThread(self, duration:float, step:float) -> None:
        fl = Thread(target=self.__fileListenerStreamThread, args=(duration, step,))
        fw = Thread(target=self.__fileWhisperStreamThread, args=(step,))
        self.flThreadIsWork = True
        fl.start()
        time.sleep(0.01)
        self.fwThreadIsWork = True
        fw.start()
 

    def __analyzeFileStreamWithoutThread(self, duration:float, step:float) -> None:
        prefix = 0
        while (prefix < self.noSections):
            self.__createTmpSoundFile(prefix, duration)
            self.__fileWhisperAnalyze(prefix)
            time.sleep(step)
            prefix += step

def startWaProcess():
    wa = WhisperAnalysier(model_size="large-v2")
    wa.analyzeWithThread(input_type="file", duration=3, step=1)

if __name__ == "__main__":
    wap = Process(target=startWaProcess)
    wap.start()
    wap.join()