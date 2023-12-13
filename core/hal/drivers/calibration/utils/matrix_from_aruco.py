import cv2
import numpy as np
from cv2 import aruco

ARUCO_SIZE = 106

def get_aruco_data(image: np.ndarray) -> dict:
    """
    Find Aruco markers in an image.

    Parameters
    ----------
    image : numpy.ndarray
        The input image.

    Returns
    -------
    list, optional
        A list of coordinates representing the detected Aruco markers.
    """

    if image is None:
        return {
            "ids": [],
            "coords": []
        }

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
    parameters =  aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)

    image_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image_gray)

    if markerIds is None or markerCorners is None:
        return {
            "ids": [],
            "coords": []
        }

    return {
        "ids": markerIds,
        "coords": list(markerCorners)
    }


def get_display_camera_projection_matrix(image: np.ndarray, aruco_display_coords: list) -> dict:
    """
    Get the transformation matrix from the camera to the projector.

    Parameters
    ----------
    image : numpy.ndarray
        The input image.
    aruco_display_coords : list
        The positions of the aruco markers on the display.

    Returns
    -------
    dict
        The transformation matrix.
    """
    aruco_data = get_aruco_data(image)

    if not aruco_data["coords"]:
        return {
            "ids": [],
            "coords": [],
            "display_to_camera_matrix": [],
            "camera_to_display_matrix": []
        }


    aruco_ids = aruco_data["ids"].flatten().tolist()
    aruco_coords = [coords.tolist()[0] for coords in aruco_data["coords"]]

    if max(aruco_ids) >= len(aruco_display_coords):
        return {
            "ids": aruco_ids,
            "coords": aruco_coords,
            "display_to_camera_matrix": [],
            "camera_to_display_matrix": []
        }

    aruco_coords_to_process = [coords[0] for i, coords in enumerate(aruco_coords)]
    aruco_display_coords = [aruco_display_coords[id] for id in aruco_ids]
    aruco_display_coords = [coords[0] for i, coords in enumerate(aruco_display_coords)]
    # aruco_coords_to_process = [[sum([coord[0]/4.0 for coord in coords[:4]]), sum([coord[1]/4.0 for coord in coords[:4]])] for i, coords in enumerate(aruco_coords)]
    # aruco_display_coords = [[sum([coord[0]/4.0 for coord in coords[:4]]), sum([coord[1]/4.0 for coord in coords[:4]])] for i, coords in enumerate(aruco_display_coords)]

    if len(aruco_coords_to_process) != 4:
        return {
            "ids": aruco_ids,
            "coords": aruco_coords,
            "display_to_camera_matrix": [],
            "camera_to_display_matrix": []
        }

    display_to_camera_matrix = cv2.findHomography(np.float32(aruco_display_coords), np.float32(aruco_coords_to_process))[0]
    camera_to_display_matrix = cv2.findHomography(np.float32(aruco_coords_to_process), np.float32(aruco_display_coords))[0]

    # print(display_to_camera_matrix)

    return {
        "ids": aruco_ids,
        "coords": aruco_coords,
        "display_to_camera_matrix": display_to_camera_matrix.tolist(),
        "camera_to_display_matrix": camera_to_display_matrix.tolist()
    }


def get_display_focus_projection_matrix(display_coords: list, focus_coords: list) -> dict:
    """
    Get the transformation matrix from the display to the focus area.

    Parameters
    ----------
    coords : dict
        The positions of the display corners in the display space.
    focus_coords : dict
        The positions of the focus area corners in the display space.

    Returns
    -------
    dict
        The transformation matrix.
    """

    if len(display_coords) != 4 or len(focus_coords) != 4:
        return {
            "display_to_focus_matrix": [],
            "focus_to_display_matrix": []
        }

    display_to_focus_matrix = cv2.getPerspectiveTransform(np.float32(display_coords), np.float32(focus_coords))
    focus_to_display_matrix = cv2.getPerspectiveTransform(np.float32(focus_coords), np.float32(display_coords))

    return {
        "display_to_focus_matrix": display_to_focus_matrix.tolist(),
        "focus_to_display_matrix": focus_to_display_matrix.tolist()
    }
