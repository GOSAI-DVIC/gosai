# GOSAI Speech to Text Module

## Overview
The Speech to Text module in GOSAI utilizes OpenAI's Whisper model to accurately transcribe speech into text. This functionality is crucial for augmented reality applications in GOSAI, enabling dynamic voice interactions with users.

## The Model
Whisper has several implementations, each focused on optimizing inference speed. The `faster-whisper` implementation provides impressive inference speed across various audio file sizes. `Faster-whisper` is a reimplementation of the Whisper model using CTranslate2, an efficient inference engine for Transformer models.

### Model Download
Before using the Speech to Text module, it is necessary to download the `faster-whisper` model. Execute the `faster_whisper_download_model.py` script to download and set up the required model files:

```bash
python faster_whisper_download_model.py
```

## Using the Module in GOSAI Applications
Integrate the Speech to Text module into your GOSAI application with the following steps:

### Module Registration
Include this in the `init` method of your application to register the module:

```python
self.requires["speech_to_text"] = ["transcription"]
```

### Performing Transcription
Use the `transcribe` method to transcribe speech:

```python
self.execute("speech_to_text", "transcribe", {"audio_buffer": audio_array})
```

**Note:** `audio_array` should be an array of `float32` with a sample rate of 16000Hz.

### Receiving Transcription Results
After the transcription process, the "transcription" event will provide the following data to your application:

```json
{
    "transcription_segments": transcription,
    "audio_duration": audio_duration,
    "transcription_duration": inference_duration
}
```

`transcription` contains the textual transcription of the audio, `audio_duration` is the length of the audio clip, and `transcription_duration` is the time taken for the transcription process.
