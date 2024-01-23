# GOSAI Speech Activity Detection Module

## Overview
The Speech Activity Detection module in GOSAI is a critical component that efficiently detects the presence of speech in audio streams. This module distinguishes speech segments from silences and ambient noise, ensuring that GOSAI processes only relevant speech data. Utilizing this module allows GOSAI to save considerable time and computing resources by avoiding unnecessary processing of non-vocal audio segments.

## The Model
This module leverages SileroVAD, a highly accurate and lightweight model specifically designed for voice activity detection tasks. SileroVAD has been trained on extensive corpora covering over 100 languages and performs robustly across various audio domains, background noises, and quality levels. Notably, SileroVAD offers rapid real-time inference capabilities: processing one audio chunk (30+ ms) takes less than 1ms on a single CPU thread. The integration of SileroVAD into GOSAI ensures a reliable foundation for precise and responsive voice analysis, essential for interactive augmented reality applications.

## Using the Module in GOSAI Applications
To use the Voice Activity Detection module within GOSAI, refer to the following guidelines:

### Module Registration
To register for the VAD module, include the following in the `init` method of your application:
```python
self.requires["speech_activity_detection"] = ["activity"]
```

### Predicting Voice Activity
The primary method for running SileroVAD inference is `predict`. To apply it on an audio array, use:
```python
self.execute("speech_activity_detection", "predict", {"audio_buffer": audio_array})
```
**Note:** The `audio_array` should be an array of `float32` with a sample rate of 16000Hz.

### Receiving Prediction Results
Once the prediction is made, your application will receive an object from the "activity" event with the following structure:
```json
{
    "confidence": speech_prob,
}
```
Here, `speech_prob` represents the speech activity probability, ranging from 0 to 1.