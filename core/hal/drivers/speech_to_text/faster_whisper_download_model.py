from faster_whisper.transcribe import WhisperModel
"""
Script to download faster whisper model
Can't be downloaded in multi-threading with python 3.10
"""
pipe = WhisperModel(model_size_or_path = 'medium.en',download_root='core/hal/drivers/speech_to_text/models' , device="cuda", compute_type="int8")