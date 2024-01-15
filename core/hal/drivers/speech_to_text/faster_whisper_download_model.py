from faster_whisper.transcribe import WhisperModel
import torch
import numpy as np
import logging

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
"""
Script to download faster whisper model
Can't be downloaded in multi-threading with python 3.10
"""
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = WhisperModel(model_size_or_path = 'medium.en',download_root='core/hal/drivers/speech_to_text/models' , device=device, compute_type="int8")
segments, info = pipe.transcribe(np.array([1, 2, 3, 4]), beam_size = 5)


#test model
test = WhisperModel(model_size_or_path = 'core/hal/drivers/speech_to_text/models/models--Systran--faster-whisper-medium.en/snapshots/a29b04bd15381511a9af671baec01072039215e3', device=device, compute_type="int8")
segments, info = test.transcribe(np.array([1, 2, 3, 4]), beam_size = 5)
