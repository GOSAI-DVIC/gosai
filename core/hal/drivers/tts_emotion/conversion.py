from core.hal.drivers.driver import BaseDriver
import torch
from TTS.api import TTS
from core.hal.drivers.emotion_conversion.utils.utils import (
    get_all_different_utt_id,
    tsv_per_emotion,
    get_tsv_lines_for_utt_ids,
    get_spker_id,
    call
)
import os
import soundfile as sf
from librosa import resample
import glob
import shutil


"""
emotion:
Neutral
Angry
Disgusted
Sleepy

possible voice:
sam
jenie
bea
josh
"""
system_path = "/home/arcadia/createch/gosai-dev"

file_path = "fairseq/examples/emotion_conversion/data"
model_dir = "fairseq/examples/emotion_conversion/models"
token_path = "fairseq/examples/emotion_conversion/processed_data_test"
user_dir = "fairseq/examples/emotion_conversion/fairseq_models"

dataset_path = "dataset_test"
final_conversion_dataset_path = "output_dataset"
final_dataset_path = "final_dataset"

class Driver(BaseDriver):

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.type = "no_loop" # no loop driver
        #create driver event
        self.create_event("audio_with_conversion")
        


    def pre_run(self):
        # runs to do at the start of the driver
        super().pre_run()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # load tts model
        self.tsv_lines = open("fairseq/examples/emotion_conversion/data/data.tsv", "r").readlines() # data tsv file with all the audio files and the number of sample associated
        self.root, self.tsv_lines = os.path.join(system_path, "dataset"), self.tsv_lines[1:]
        self.utts = get_all_different_utt_id(self.tsv_lines)
        tts = TTS("tts_models/en/ljspeech/fast_pitch").to(device)

        # create a list of path with all the speaker wav

        self.create_callback("tts_emotion_conversion", self.tts_with_conversion)

    def tts_with_conversion(self, data):
        """

        entry: dict["text": str, "emotion": str, "character": str]
        return audio: np.array
        """

        utts = get_all_different_utt_id(self.tsv_lines)
        os.makedirs(os.path.join(dataset_path, data["character"], "Neutral"), exist_ok=True)
            
        character = data["character"]
        specific_utt = utts[character].pop()
        name_audio = f"target_{specific_utt}.wav"
        audio_path = os.path.join(dataset_path, f"{character}/Neutral",name_audio)
        print(audio_path)
        
        #Creation of the audio file

        self.tts.tts_to_file(data["text"], file_path=audio_path)
        
        #Resample the audio file
        data, samplerate = sf.read(audio_path)
        data = resample(data,orig_sr = samplerate, target_sr = 16000)
        sf.write(audio_path, data, 16000)
        name = os.path.join(f"{character}/Neutral",name_audio)
        line = f"{name}\t{len(data)}\t\n"
        lines.append(line)

        #save the line for the tsv
        tsv_lines_emotion = tsv_per_emotion(self.tsv_lines, data["emotion"])
        tsv_lines_utt = get_tsv_lines_for_utt_ids(tsv_lines_emotion,specific_utt)
        for x in tsv_lines_utt:
            if x[-2:]!="\n" and x[:3]=="sam":
                x+="\n"
        print(tsv_lines_utt)
    
        #copy the audio of the tsv
        for line in tsv_lines_utt:
            if get_spker_id(line) == character:
                lines += [line]
                os.makedirs(os.path.join(dataset_path, character, emotion), exist_ok=True)
                shutil.copy(os.path.join(self.root, line.split("\t")[0]), os.path.join(dataset_path, line.split("\t")[0]))
            
        #save the tsv
        lines = [dataset_path + "\t\n"] + lines
        lines = lines[:-1] + [lines[-1][:-1]]
        open(os.path.join(file_path, "data.tsv"), "w").writelines(lines)
        emotion = data["emotion"]
        call(
            model_dir=os.path.join(system_path, model_dir),
            data=os.path.join(system_path, file_path),
            split="data",
            output_path=os.path.join(system_path, token_path),
            src_emotion="neutral",
            trg_emotion=emotion.lower(),
            dict=os.path.join(system_path, dataset_path, "dict.txt"),
            user_dir=os.path.join(system_path, user_dir),
            dataset=os.join.path(system_path, final_conversion_dataset_path, f"{emotion.lower()}")
        )
        if os.path.exists(os.path.join(system_path, final_conversion_dataset_path, f"{emotion.lower()}", name_audio)):
            audio, rate = sf.read(os.path.join(system_path, final_conversion_dataset_path, f"{emotion.lower()}", name_audio))
            self.set_event_data("audio_with_conversion", audio)
        else:
            audio = self.tts.tts(data['text'])
            self.set_event_data("audio_with_conversion", audio)



