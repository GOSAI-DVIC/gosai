from core.hal.drivers.driver import BaseDriver
import numpy as np
from scipy.signal import resample
from core.hal.drivers.speech_to_text.fast_whisper.fast_whisper import WhisperModel
import time

import io 
import av
from typing import BinaryIO, List, NamedTuple, Optional, Tuple, Union, Iterable
import itertools
import gc

from scipy.io.wavfile import write



#core.hal.drivers.speech_to_text.fast_whisper.
class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        #create driver event
        # self.register_to_driver("microphone", "audio_stream")
        # self.register_to_driver("speech_activity_detection", "activity")

        self.create_event('transcription')
        

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.blocks = []

        self.model = WhisperModel("medium.en", device="cuda", compute_type="int8")

        self.create_callback("transcribe", self.transcribe)


    def transcribe(self, data):
        start = time.time()

        audio = data["full_audio"]

        save_audio(audio)

        #print(len(audio))
        #print(f'duration audio is {len(audio)/16000}s')

        #audio_bis = decode_audio('test_bis.wav')
        #self.model = WhisperModel("medium.en", device="cpu", compute_type="int8")
        self.log("transcription",3)
        print(len(audio)/16000)

        segments = self.model.transcribe(np.array(audio), beam_size = 5)

        self.log("self.model.transcribe",3)
        
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        self.log("finished printing segments",3)
        print('durée : ', time.time() - start)
   

def save_audio(audio):
    audio_int16 = np.int16(audio/np.max(np.abs(audio)) * 32767)
    write('test.wav', 16000, audio_int16)



def _ignore_invalid_frames(frames):
    iterator = iter(frames)

    while True:
        try:
            yield next(iterator)
        except StopIteration:
            break
        except av.error.InvalidDataError:
            continue


def _group_frames(frames, num_samples=None):
    fifo = av.audio.fifo.AudioFifo()

    for frame in frames:
        frame.pts = None  # Ignore timestamp check.
        fifo.write(frame)

        if num_samples is not None and fifo.samples >= num_samples:
            yield fifo.read()

    if fifo.samples > 0:
        yield fifo.read()


def _resample_frames(frames, resampler):
    # Add None to flush the resampler.
    for frame in itertools.chain(frames, [None]):
        yield from resampler.resample(frame)

def decode_audio(
    input_file: Union[str, BinaryIO],
    sampling_rate: int = 16000,
    split_stereo: bool = False,
):
    """Decodes the audio.

    Args:
      input_file: Path to the input file or a file-like object.
      sampling_rate: Resample the audio to this sample rate.
      split_stereo: Return separate left and right channels.

    Returns:
      A float32 Numpy array.

      If `split_stereo` is enabled, the function returns a 2-tuple with the
      separated left and right channels.
    """
    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono" if not split_stereo else "stereo",
        rate=sampling_rate,
    )

    raw_buffer = io.BytesIO()
    dtype = None

    with av.open(input_file, metadata_errors="ignore") as container:
        frames = container.decode(audio=0)
        frames = _ignore_invalid_frames(frames)
        frames = _group_frames(frames, 500000)
        frames = _resample_frames(frames, resampler)

        for frame in frames:
            array = frame.to_ndarray()
            dtype = array.dtype
            raw_buffer.write(array)

    # It appears that some objects related to the resampler are not freed
    # unless the garbage collector is manually run.
    del resampler
    gc.collect()

    audio = np.frombuffer(raw_buffer.getbuffer(), dtype=dtype)

    # Convert s16 back to f32.
    audio = audio.astype(np.float32) / 32768.0

    if split_stereo:
        left_channel = audio[0::2]
        right_channel = audio[1::2]
        return left_channel, right_channel

    return audio

# if __name__ == '__main__' :

#     model = WhisperModel("medium.en", device="cuda", compute_type="int8")