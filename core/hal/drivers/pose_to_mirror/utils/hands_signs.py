import os
from typing import List

import numpy as np
import onnxruntime


SIGNS = {
    "0": "OK",
    "1": "THUMB_UP",
    "2": "TWO",
    "3": "THREE",
    "4": "SPIDERMAN",
    "5": "OPEN_HAND",
    "6": "FIST",
    "7": "PINCH",
    "8": "THUMB_DOWN",
    "9": "INDEX",
    "10": "MIDDLE",
    "11": "LITTLE",
}


def onehot(index: int, size: int = 16) -> List[int]:
    """Creates a onehot"""
    one_hot = [0 for i in range(size)]
    one_hot[index] = 1
    return one_hot


def init():
    """Import the model"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(dir_path, "models/handsign.onnx")
    model = onnxruntime.InferenceSession(model_path)
    return model
    # except:
    #     print("No model saved")
    #     return None


def find_gesture(model, data: List[List]) -> List:
    """Evaluate the data using the model"""
    ort_inputs = {model.get_inputs()[0].name: np.array(data, dtype=np.float32)}
    out = model.run(None, ort_inputs)[-1]
    return [SIGNS[str(np.argmax(out))], float(np.max(out))]


def normalize_data(data: List[List], width, height) -> List[List]:
    """Normalize the data to fit the hand sign inout data"""
    return [[x / width, y / height] for x, y, *_ in data]
