import os

import numpy as np
# pip install onnx
import onnxruntime

SLR_ACTIONS = [
    "nothing",
    "empty",
    "hello",
    "thanks",
    "iloveyou",
    "what's up",
    "hey",
    "my",
    "name",
    "nice",
    "to meet you",
]


def adapt_data(sequences: list) -> list:
    """
    Adapt data to the model
    """

    new_sequences = []
    for _, sequence in enumerate(sequences):
        pose = np.array([[res[0]/640, res[1]/480] for res in sequence["body_pose"]]).flatten(
        ) if sequence["body_pose"] else np.zeros(33*2)
        # face = np.array([[res[0], res[1], res.z] for res in sequence.face_landmarks.landmark]).flatten(
        # ) if sequence.face_landmarks else np.zeros(468*3)
        lh = np.array([[res[0]/640, res[1]/480] for res in sequence["left_hand_pose"]]).flatten(
        ) if sequence["left_hand_pose"] else np.zeros(21*2)
        rh = np.array([[res[0]/640, res[1]/480] for res in sequence["right_hand_pose"]]).flatten(
        ) if sequence["right_hand_pose"] else np.zeros(21*2)
        new_sequences.append(np.concatenate([pose, lh, rh]))

    return new_sequences


def init():
    """
    Initialize the module
    """
    input_size = 150
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #dummy_input = torch.randn(30, input_size, requires_grad=True)

    model_path = os.path.join(dir_path, "../models/slr.onnx")
    model = onnxruntime.InferenceSession(model_path)
    return model
    # model = onnx.load_state_dict(state_dict)
    # torch.onnx.export(model, dummy_input, "action.onnx")
    # onnx.save(model, dir_path + "models/")
    # #model = onnxruntime.InferenceSession(model_path)
    # return model


def get_sign(model, frames: list) -> list:
    """
    Get sign from frames
    """
    data = adapt_data(frames)
    ort_inputs = {model.get_inputs()[0].name: np.array([data], dtype=np.float32)}
    out = model.run(None, ort_inputs)[-1]
    out = np.exp(out) / np.sum(np.exp(out))
    return (SLR_ACTIONS[np.argmax(out)], float(np.max(out)))
