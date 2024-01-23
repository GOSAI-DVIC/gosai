# GOSAI Speaker Recognition Module

## Overview
GOSAI's Speaker Recognition module is adept at authenticating user identity using voice. This module employs advanced modeling to generate an embedding that captures unique features of a speaker's voice. These embeddings are then used to calculate the similarity (using cosine distance) between voices, enabling precise identification of individuals. This capability is crucial for applications that demand secure identity recognition and user-based personalization.

## The Model
The module utilizes the CAM++ model for extracting voice embeddings. CAM++ has shown superior efficiency compared to other models like Resnet or ECAPA-TDNN. It excels in accurately capturing voice features for reliable speaker recognition.

## Using the Module in GOSAI Applications
Integration and usage of the Speaker Recognition module within GOSAI involve the following steps:

### Module Registration
To register for the speaker recognition module, include this in your application's `init` method:
```python
self.requires["speech_speaker_extraction"] = ["speaker_emb"]
```

### Performing Speaker Recognition
To run CAM++ inference, use the `speaker_verification` method:
```python
self.execute("speech_speaker_extraction", "speaker_verification", {"audio_buffer": audio_array, "new_user": True})
```
**Note:** `audio_array` must be an array of `float32` with a sample rate of 16000Hz. `new_user`: If set to True, the predicted embedding will be saved by the module. If False, the predicted embedding will be compared to all saved embeddings.

### Receiving Prediction Results
Upon completion of the prediction, your application will receive an object from the "speaker_emb" event with:
```json
{
    "embedding": embedding,
    "comparaison": results
}
```
`embedding` is the predicted embedding from the audio, and `results` is a dictionary containing all saved embeddings and their distance scores with the predicted embedding, ranging from 0 to 1.
