import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from model import LSTM
from data import SignCollection, load
from utils import onehot
import random 

import onnxruntime
import numpy as np





def export_to_onnx():
    """ Exports the pytorch model to onnx """
    DATA = "data/trainning.csv"
    sign_data = load(DATA)
    sign_collection = SignCollection(sign_data)

    model = LSTM()
    model.load_state_dict(torch.load("saves/handsign.pt"))
    model.eval()
    input = sign_collection[0][1]
    torch_out = model(input)

    torch.onnx.export(
        model,
        input,
        "saves/handsign.onnx",
        export_params=True,
        opset_version=10,
        do_constant_folding=True,
        input_names = ['input'],
        output_names = ['output'],
        dynamic_axes={'input' : {0 : 'batch_size'},
                    'output' : {0 : 'batch_size'}})

    ort_session = onnxruntime.InferenceSession("saves/handsign.onnx")




    import random
import numpy as np
from typing import Dict, List, Tuple
import cv2 as cv

import torch
from torch.utils.data import DataLoader, Dataset

from utils import onehot


class SignCollection(Dataset):
    def __init__(self, signs_data: List[Dict]) -> None:
        super(SignCollection, self).__init__()
        self.data = signs_data

    def __len__(self) -> int:
        return len(self.data)*10

    def __getitem__(self, idx: int) -> Tuple[torch.FloatTensor, torch.Tensor]:
        idx = idx % len(self.data)
        id, data = self.data[idx]["id"], self.data[idx]["data"]
        # Random scale from center
        horizontal_min, horizontal_max = np.min(data, axis=0)[0], np.max(data, axis=0)[0]
        vertical_min, vertical_max = np.min(data, axis=0)[1], np.max(data, axis=0)[1]
        center = self.data[idx]["center"]
        max_hori_scale = min(center[0]/(center[0] - horizontal_min), (1 - center[0])/(horizontal_max - center[0]))
        max_vert_scale = min(center[1]/(center[1] - vertical_min), (1 - center[1])/(vertical_max - center[1]))
        x_scale = random.uniform(
            0.1, min(max_hori_scale, max_vert_scale)
        )
        if random.random() > 0.5:
            y_scale = random.uniform(0.75, 1) * x_scale
        else:
            y_scale = x_scale
            x_scale = random.uniform(0.75, 1) * y_scale
        data = [
            [
                (point[0] - center[0]) * x_scale + center[0],
                (point[1] - center[1]) * y_scale + center[1],
            ]
            for point in data
        ]

        # Random centered rotate
        angle = random.uniform(-np.pi, np.pi)
        data = [
            [
                center[0] + (point[0] - center[0]) * np.cos(angle) - (point[1] - center[1]) * np.sin(angle),
                center[1] + (point[0] - center[0]) * np.sin(angle) + (point[1] - center[1]) * np.cos(angle),
            ]
            for point in data
        ]

        # Random translate
        horizontal_min, horizontal_max = np.min(data, axis=0)[0], np.max(data, axis=0)[0]
        vertical_min, vertical_max = np.min(data, axis=0)[1], np.max(data, axis=0)[1]
        horizontal_translate = random.uniform(-horizontal_min, 1-horizontal_max)
        vertical_translate = random.uniform(-vertical_min, 1-vertical_max)
        data = [
            [point[0] + horizontal_translate, point[1] + vertical_translate]
            for point in data
        ]

        return id, torch.tensor(data, dtype=torch.float32)
        # return torch.tensor(onehot(id), dtype=torch.float32), torch.tensor(data, dtype=torch.float32)


def load(path):
    result = []
    with open(path, "r") as f:
        file_data = f.readlines()
        for line in file_data:
            line = line.strip("\n").split(";")
            index = int(line[0])
            data = []
            r_data = []
            for pair in line[1:]:
                pair = pair.split(",")
                data.append([float(pair[0]), float(pair[1])])
                r_data.append([1 - float(pair[0]), float(pair[1])])
            center = [0, 0]
            for d in data:
                center[0] += d[0]
                center[1] += d[1]
            center[0] /= len(data)
            center[1] /= len(data)

            result.append(
                {
                    "id": index,
                    "data": data,
                    "center": center,
                }
            )
            result.append(
                {
                    "id": index,
                    "data": r_data,
                    "center": [1 - center[0], center[1]],
                }
            )
    return result


def view_data():
    DATA = "data/trainning.csv"
    sign_data = load(DATA)
    sign_collection = SignCollection(sign_data)
    for index, sign in enumerate(sign_collection):
        # Create blanck image
        img = np.zeros((800, 800, 3), np.uint8)
        # Draw data
        for i, point in enumerate(sign[1]):
            cv.circle(img, (int(point[0] * 800), int(point[1] * 800)), 3, (255, 255, 255), -1)
            # Show point index
            cv.putText(
                img,
                str(i),
                (int(point[0] * 800) + 5, int(point[1] * 800) + 5),
                cv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
        # Show sign index
        cv.putText(img, str(sign[0]), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        # Show frame index
        cv.putText(img, str(index), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        # Show image
        cv.imshow("image", img)
        key = cv.waitKey(0) & 0xFF
        if key == ord("q"):
            break

