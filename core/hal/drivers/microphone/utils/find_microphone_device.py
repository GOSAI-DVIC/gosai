import sounddevice as sd

def find_microphone_device() -> int:
    """
    Find the index of the microphone device to use.
    To do so, we use the query function to get the name of all the devices and their number by their position in the device list.
    We have a priority device list which we have to if they exist in the list
    return: the index of the microphone device to use.
    """
    liste_device_name = [device['name'] for device in sd.query_devices()]
    priority_device = ['pipewire', 'pulse']
    for priority in priority_device:
        if priority in liste_device_name:
            return liste_device_name.index(priority)
    return sd.default.device[0]


def get_microphone_configuration(config: dict)->tuple[int, int, int]:
    """
    Get the configuration of the microphone from the config.json file.
    return: a tuple with the device index, the samplerate and the channels
    """
    if 'microphone' not in config.keys():
        return find_microphone_device(), sd.query_devices(kind='input')['default_samplerate'], 1
    else:
        device_index = config['microphone']['number'] if 'number' in config['microphone'].keys() else find_microphone_device()
        samplerate = config['microphone']['samplerate'] if 'samplerate' in config['microphone'].keys() else sd.query_devices(device_index, kind='input')['default_samplerate']
        channels = config['microphone']["channels"] if "channels" in config['microphone'].keys() else 1
    return device_index, samplerate, channels