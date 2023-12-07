from faster_whisper.transcribe import WhisperModel

#model_size = "core/hal/drivers/speech_to_text/models/medium.en"

            # Run on GPU with FP16
pipe = WhisperModel(model_size_or_path = 'medium.en',download_root='models' , device="cuda", compute_type="int8")