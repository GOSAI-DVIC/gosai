import os

import numpy as np
# pip install onnx
import onnxruntime
import onnxruntime as ort
import time

def adapt_data(frame: list) -> list:
    """
    Adapt data to the model
    image shape[0] = 480
    frape.shape[1] = 640
    """
    

    pose = np.array([[res[0], res[1]] for res in frame["body_pose"]]).flatten(
        ) if frame["body_pose"] else np.zeros(33*2)
    lh = np.array([[res[0], res[1]] for res in frame["left_hand_pose"]]).flatten(
    ) if frame["left_hand_pose"] else np.zeros(21*2)
    rh = np.array([[res[0], res[1]] for res in frame["right_hand_pose"]]).flatten(
    ) if frame["right_hand_pose"] else np.zeros(21*2)  
    return np.concatenate([pose, lh, rh])

def init(output_size):
    """
    Initialize the module
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #dummy_input = torch.randn(30, input_size, requires_grad=True)

    model_path = os.path.join(dir_path, "../models/slr_"+str(output_size)+".onnx")
    model = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    return model


def get_sign(model, sequence, actions) -> list:
    """
    Get sign from frames
    """
    #print("input shape: ", np.array([sequence], dtype=np.float32).shape)
    #ort_inputs = {'input': np.array(
    ort_inputs = {'input': np.array(
    [sequence], dtype=np.float32)}
    out = model.run(None, ort_inputs)[-1]
    out = np.exp(out) / np.sum(np.exp(out))
    return (actions[np.argmax(out)], float(np.max(out)))