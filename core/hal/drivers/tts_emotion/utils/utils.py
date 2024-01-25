from subprocess import check_call


def get_fname(s):
    return s.split("\t")[0]

def get_emotion(s):
    return get_fname(s).split("_")[0].split("/")[1].lower()
def get_spker_id(s):
    return get_fname(s).split("_")[0].split("/")[0].lower()

def get_utt_id(s):
    return get_fname(s).split(".")[0].split("_")[-1]
def get_all_different_utt_id(tsv_lines) -> list:
    utts_per_speaker = {
    "sam": [],
    "bea": [],
    "josh": [],
    "jenie": [],
    }
    for line in tsv_lines:
        spkr = get_spker_id(line)
        utt_id = get_utt_id(line)
        if utt_id not in utts_per_speaker[spkr]:
            utts_per_speaker[spkr].append(utt_id)
    return utts_per_speaker
def tsv_per_emotion(tsv_lines, emotion) -> list:
    lines = []
    for line in tsv_lines:
        if emotion.lower() == get_emotion(line):      
            lines.append(line)      
    return lines
def get_tsv_lines_for_utt_ids(tsv_lines, specific_utt_id):
    utts_per_speaker = []
    for line in tsv_lines:
        spkr = get_spker_id(line)
        utt_id = get_utt_id(line)
        if utt_id == specific_utt_id:
            # Assuming the audio file name is also part of the line, extract it
            utts_per_speaker.append(line)

    return utts_per_speaker
def get_tsv_lines_for_emotion(tsv_lines, emotion):
    audio_files_name = []

    for line in tsv_lines:
        if emotion == get_emotion(line):
            # Assuming the audio file name is also part of the line, extract it
            audio_files_name.append(line)

    return audio_files_name
def get_number_audio_per_emotion(df, emotion):
    return len(df[df['emotion'] == emotion])

def sample_and_remove_rows(df, num_rows):
    # Randomly sample rows
    sampled_rows = df.sample(n=num_rows)

    # Remove sampled rows from the original DataFrame
    df.drop(sampled_rows.index, inplace=True)

    return sampled_rows, df
def decompose_base_2(number):
    powers = []
    remainder = number
    power = 0

    # Find the highest power of 2 less than or equal to the number
    while 2 ** power <= number:
        power += 1

    # Subtract powers of 2 from the number and store them
    for i in range(power - 1, -1, -1):
        if 2 ** i <= remainder:
            powers.append(2 ** i)
            remainder -= 2 ** i

    return powers
def call(
    model_dir,
    data,
    split,
    output_path,
    src_emotion,
    trg_emotion,
    dict,
    user_dir,
    dataset
):
    cmd = f"""python3 fairseq/examples/emotion_conversion/preprocessing.py \
    --model-dir {model_dir} \
    --data {data} \
    --split {split} \
    --output-path {output_path} \
    --src-emotion {src_emotion} \
    --trg-emotion {trg_emotion} \
    --dict {dict} \
    --user-dir {user_dir} \
    --dataset {dataset}"""
    
    check_call(cmd, shell=True)