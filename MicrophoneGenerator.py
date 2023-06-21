import pyaudio
import wave
from threading import Thread
import keyboard 
import time
import queue

class MicrophoneGenerator():
    def __init__(self, input_device_index = 0, channels = 1, chunk = 1024, sample_format = pyaudio.paInt16, rate=44100, prefixDevider = 40) -> None:
        self.channels = channels
        self.chunk = chunk
        self.sample_format = sample_format
        self.rate = rate
        self.p = pyaudio.PyAudio()
        # self.frame_q = queue.Queue()
        self.frames = []
        self.stream = None
        self.prefix = 0
        self.prefixDevider = prefixDevider
        self.isRecording = False
        self.input_device_index = input_device_index

    def start_stream(self) -> None:
        self.prefix = 0
        self.stream = self.p.open(format=self.sample_format,
        channels=self.channels,
        rate=self.rate,
        frames_per_buffer=self.chunk,
        input_device_index=self.input_device_index, # индекс устройства с которого будет идти запись звука 
        input=True)

    def __recordThread(self, duration, step) -> None:
        print("start recording")
        while self.isRecording:
            self.__createTempFiles(duration, step)

    def record(self, duration = 3, step = 1.5) -> None:
        t = Thread(target=self.__recordThread, args=(duration, step,))
        t.daemon = True
        self.isRecording = True
        t.start()

    def recordOneTime(self, duration = 3, step = 1.5) -> None:
        self.isRecording = True
        print("start recording")
        self.__createTempFiles(duration, step)
        self.isRecording = False



    def __createTempFile(self) -> str:
        filename = f"sounds/test{self.prefix}.wav"
        wf = wave.open(filename, 'w')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return filename

    def __createTempFiles(self, duration:float, step:float) -> None:
        if not self.frames:
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = self.stream.read(self.chunk)
                self.frames.append(data)
            print("saving file")
            self.__createTempFile()
            if duration == step:
                self.frames = []
                self.prefix = (self.prefix + step) % self.prefixDevider
        else:
            self.prefix = (self.prefix + step) % self.prefixDevider
            self.frames = self.frames[int(self.rate / self.chunk * step): int(self.rate / self.chunk * duration)]
            for i in range(0, int(self.rate / self.chunk * step)):
                data = self.stream.read(self.chunk)
                self.frames.append(data)
            print("saving file")
            self.__createTempFile()

    def stop_recording(self):
        self.isRecording = False
        self.stop_stream()

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print('Finished recording!')


if __name__ == "__main__":
    try:
        m = MicrophoneGenerator()
        m.start_stream()
        m.record()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        m.stop_recording
        print("Thread ended")