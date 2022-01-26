x_offset = -230 # millimeters, increase to move left
y_offset = 100 #Increase to move down

screen_width = 392.85 # millimeters
screen_height = 698.4

width = 1080
height = 1920

to_mirror = [
    "body_pose",
    "right_hand_pose",
    "left_hand_pose",
    "face_mesh"
]

inter_rates = {
    "body_pose": 0.4,
    "right_hand_pose": 0.6,
    "left_hand_pose": 0.6,
    "face_mesh": 0.6
}

def mirror_data(data: dict, old_data: dict = {}) -> dict:
    """
    Mirrors the data

    :param data: The data to mirror
    :return: The mirrored data
    """
    if old_data != {}:
        return {key: (mirror_points_with_interpolation(value, old_data[key], inter_rates[key]) if key in to_mirror else value ) for key, value in data.items()}
    else:
        return {key: (mirror_points(value) if key in to_mirror else value ) for key, value in data.items()}

def mirror_points_with_interpolation(points: list, old_points: list, t: int = 0.8) -> list:
    """
    Mirrors the points using linear interpolation

    :param points: The points to mirror
    :return: The mirrored points
    """

    mirrored_points = []

    for i, point in enumerate(points):
        x = width * (point[0] - x_offset) / screen_width
        y = height * (point[1] - y_offset) / screen_height
        if len(points) == len(old_points) and t < 1:
            if(y > 0):
                x = lerp(old_points[i][0], x, t)
                y = lerp(old_points[i][1], y, t)
            else:
                x = lerp(old_points[i][0], x, 0.01)
                y = lerp(old_points[i][1], y, 0.01)

            mirrored_points.append([x, y] + point[2:])
        else:
            mirrored_points.append([x, y] + point[2:])

    return mirrored_points

def mirror_points(points: list) -> list:
    """
    Mirrors the points

    :param points: The points to mirror
    :return: The mirrored points
    """

    mirrored_points = []

    for point in points:
        x = width * (point[0] - x_offset) / screen_width
        y = height * (point[1] - y_offset) / screen_height
        mirrored_points.append([x, y] + point[2:])

    return mirrored_points

def lerp(a, b, t):
    return (1 - t) * a + t * b
