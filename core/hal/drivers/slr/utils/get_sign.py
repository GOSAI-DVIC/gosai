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

    # pose = np.array([[res[0], res[1]] for res in frame["body_pose"]]).flatten(
    #     ) if frame["body_pose"] else np.zeros(33*2)
    # lh = np.array([[res[0], res[1]] for res in frame["left_hand_pose"]]).flatten(
    # ) if frame["left_hand_pose"] else np.zeros(21*2)
    # rh = np.array([[res[0], res[1]] for res in frame["right_hand_pose"]]).flatten(
    # ) if frame["right_hand_pose"] else np.zeros(21*2)  
    # return np.concatenate([pose, lh, rh])

    pose = []
    lh = []
    rh = []
    # pose
    if frame["body_pose"]:
        for i, _ in enumerate(frame["body_pose"]):
            pose.append(frame["body_pose"][i][0])
            pose.append(frame["body_pose"][i][1])
    else:
        pose = np.zeros(33*2)

    # left hand
    if frame["left_hand_pose"]:
        for i, _ in enumerate(frame["left_hand_pose"]):
            lh.append(frame["left_hand_pose"][i][0])
            lh.append(frame["left_hand_pose"][i][1])
    else:
        lh = np.zeros(21*2)

    # right hand
    if frame["right_hand_pose"]:
        for i, _ in enumerate(frame["right_hand_pose"]):
            rh.append(frame["right_hand_pose"][i][0])
            rh.append(frame["right_hand_pose"][i][1])
    else:
        rh = np.zeros(21*2)

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
    ort_inputs = {'input': np.array(
    [sequence], dtype=np.float32)}
    out = model.run(None, ort_inputs)[-1]
    out = np.exp(out) / np.sum(np.exp(out))
    return (actions[np.argmax(out)], float(np.max(out)))