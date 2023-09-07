import sounddevice as sd

def find_speaker_device() -> int:
    """
    Find the index of the speaker device to use.
    To do so, we use the query function to get the name of all the devices and their number by their position in the device list.
    We have a priority device list which we have to if they exist in the list
    return: the index of the speaker device to use.
    """
    liste_device_name = [device['name'] for device in sd.query_devices()]
    priority_device = ['pipewire', 'pulse']
    for priority in priority_device:
        if priority in liste_device_name:
            return liste_device_name.index(priority)
    return sd.default.device[0]


def get_speaker_configuration(config: dict)->tuple[int, int, int, int]:
    """
    Get the configuration of the speaker from the config.json file.
    return: a tuple with the device index, the samplerate, the channels and the blocksize
    """
    if 'speaker' not in config.keys():
        return find_speaker_device(), sd.query_devices(kind='input')['default_samplerate'], 1, 2048
    else:
        device_index = config['speaker']['number'] if 'number' in config['speaker'].keys() else find_speaker_device()
        samplerate = config['speaker']['samplerate'] if 'samplerate' in config['speaker'].keys() else sd.query_devices(device_index, kind='outputs')['default_samplerate']
        channels = config['speaker']["channels"] if "channels" in config['speaker'].keys() else 1
        blocksize = config['speaker']["blocksize"] if "blocksize" in config['speaker'].keys() else 2048
    return device_index, samplerate, channels, blocksize
