import numpy as np
from multiprocessing import Process, freeze_support
from faster_whisper import WhisperModel
import time
import os
import datetime
import soundfile as sf
import random

class WhisperAnalysier():
    def __init__(self, model_size = "base", model_type="cuda", transcribe_file="transcript.txt") -> None:
        if model_type == "cuda":
            try:
                self.model = WhisperModel(model_size, device="cuda", compute_type="float16", cpu_threads=6)
            except:
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=6)
        else:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=6)
        self.data = None
        self.samplerate = None
        self.noSections = None
        self.transcribe_file =  transcribe_file
        self.processes_dict = dict()

    def __fileWhisperAnalyze(self, path, remove):
        now = datetime.datetime.now()
        # rnd = random.randint(0, 10000)
        filename = path
        # if os.path.exists(filename):
        segments, _ = self.model.transcribe(filename, language="ru", initial_prompt="Phone call", best_of=1, beam_size=1, condition_on_previous_text= False) #max_initial_timestamp=0.5
        text_l = ""
        for segment in segments:
            if segment.no_speech_prob > 0.8:
                text_i = ""
            else:
                text_i = segment.text
                text_l += text_i
            # with open(self.transcribe_file, 'a', encoding='utf-8') as f:
            #     f.write(text_i)
        print(datetime.datetime.now() - now)
        if remove:
            os.remove(filename)
        return(text_l)

    def analyze(self, path = "test.wav", remove=False) -> None:
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