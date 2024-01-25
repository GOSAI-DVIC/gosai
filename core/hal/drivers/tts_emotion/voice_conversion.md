# TTS-with-emotion-conversion
Text-to-speech using emotion conversion for more immersion into theatre piece on [GOSAI](https://github.com/GOSAI-DVIC). The goal is too use the audio created by this program in an application to train for theatre when a comadian is not there. For more realisme we want to put emotion characteristic. 

## Overview
This project leverages advanced voice conversion technologies to bring life to theatrical scripts. Using the [Coqui.ai library](https://github.com/coqui-ai/TTS) for voice synthesis and the [FAIRSEQ emotion conversion tool](https://github.com/facebookresearch/fairseq/tree/main/examples/emotion_conversion), this system transforms written scripts into expressive, character-specific audio files.

# How it works

To create emotion conversion, this can’t be done directly on gosai due to the size of the module. It will be contrary to the vision of the project to make it has a module in GOSAI. however it can be done outside of the framework with this repository using the paper Textless … and fairseq environment(facebook deeplearning research framework). It use 6 different models to make emotion conversion. the two first one (Hubert and kmean) are used to extract the feature of the speech, this features are token vectors that have in information the speech and the emotion from the audio. the second step is to translate the token from an emotion A to B. Five emotion can be choosen (Neutral, Amused, Angry, Sleepy and disgusted). this translated token are now used with the output of a pitch predictor and duration predictor model that improve the realism of the output speech. An modified HiFiGAN model recreate the audio with the translated tokens and the output of the predictior models.

The first two models, Hubert and K-means, are employed to extract speech features. These features are represented as token vectors, encapsulating both the speech and its associated emotion from the audio. The next phase involves translating these tokens from one emotional state (Emotion A) to another (Emotion B). Users can choose from five emotions: Neutral, Amused, Angry, Sleepy, and Disgusted.

After the translation of tokens, the output is further enhanced by a pitch predictor and a duration predictor model, both of which contribute to the realism of the resultant speech. Finally, a modified HiFiGAN model is used to reconstruct the audio, utilizing both the translated tokens and the outputs from the predictor models to ensure a high-quality, emotionally converted speech output.

# How to use it

## Installation

Create a environment

```
python3 -m venv .venv
```

Then:

```bash
git clone https://github.com/facebookresearch/fairseq.git
cd fairseq/examples/emotion_conversion
git clone https://github.com/Arcadia24/speech-resynthesis.git
cp -r preprocess_2/ preprocess/
```
Install emoV discrete token
```bash
wget https://dl.fbaipublicfiles.com/textless_nlp/emotion_conversion/data.tar.gz  # (still in fairseq/examples/emotion_conversion)
tar -xzvf data.tar.gz
```
Go back in the main folder with fairseq and install dependencies
```bash
pip install --editable ./
pip install -r examples/emotion_conversion/requirements.txt
```
To get example audio for the emotion conversion
```bash
mkdir dataset
```
Now download emoV dataset and put it in a folde named `dataset` in main folder


Download the folder with all the weights for the model in this [Drive](https://drive.google.com/drive/folders/1TGbS2fFTbPRuXUXg4KSnx02-Fxn2iYp-) and put them in a folder name save in the emotion conversion folder
```bash
cd fairseq/examples/emotion_conversion/save
```

Now you are ready to use it like a normal driver!

## Use it in your application

Start the driver the init part of the application

```python
self.requires["emotion_conversion"] = ["conversion"]
```

To convert an audio use:

```python
data = {
    "text" : self.scene_script['sentence'].iloc[idx], 
    "emotion" : self.dico_speaker[char],
    "character"
    }
self.execute("emotion_conversion", "make_conversion", )
```

the datat will be received with this line in the listener:

```python
 if source == "tts_emotion" and event == "audio_with_conversion" and data is not None:
    ...
```
## Audio Example
You can listen to some examples of audio generated

[Audio Example](https://drive.google.com/drive/folders/1HnyVwVjERHKs_aIR7H0eZaWzWf-23UlO?usp=sharing)
