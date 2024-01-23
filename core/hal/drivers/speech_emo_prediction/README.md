# GOSAI Speech Emotion Prediction Module

## Overview
The Speech Emotion Prediction module in GOSAI is designed to interpret emotions from spoken words. It supports various emotions including Neutral, Disgust, Fear, Sadness, Anger, and Happiness. This module enables applications to respond in a contextually and empathetically appropriate manner, providing a highly personalized and engaging user experience.

## The Model
This module utilizes a fine-tuned version of Wav2vec2, a model that functions similarly to BERT, for speech emotion classification. Wav2Vec2 takes an audio signal as input and provides a representation of the raw audio waveform, containing both acoustic and linguistic information. Originally pre-trained for ASR (Automatic Speech Recognition) tasks, the model is adept at extracting crucial acoustic information. When fine-tuned for ESR (Emotion Speech Recognition), its attention layers learn to unveil linguistic cues pertinent to emotion recognition.

## Using the Module in GOSAI Applications
To integrate the Speech Emotion Prediction module in GOSAI, follow these instructions:

### Module Registration
To register for the emotion prediction module, include the following in the `init` method of your application:
```python
self.requires["speech_emo_extraction"] = ["speech_emotion"]
```

### Predicting Emotion
The primary method for running Wav2vec2 inference is `predict`. To apply it on an audio array, use:
```python
self.execute("speech_emo_extraction", "predict", {"audio_buffer": audio_array})
```
**Note:** The `audio_array` should be an array of `float32` with a sample rate of 16000Hz.

### Receiving Prediction Results
Once the prediction is made, your application will receive an object from the "speech_emotion" event with the following structure:
```json
{
    "results" : emo_prob,
}
```
Here, `emo_prob` is a dictionary with the probability associated with each emotion class.
