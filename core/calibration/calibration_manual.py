import numpy as np
import cv2
from itertools import permutations  
import json

l_point_test = [[450,600],[450,850],[1250,600],[1230,850]]
#l_point_test = [[400,300],[400,780],[1520,300],[1520,780]] #Original test coords
screen_coords=[[0,0], [0,1080],[1920,0],[1920,1080]]

############### Setting Importation ###############

try:
    with open('home/calibration_data.json', 'r') as f:
        data = json.load(f)

    camera_distortion = np.float32(data["camera_distortion"])
    for k,v in data.items():
        globals()[k]=np.array(v)
    # print("Calibraton Data:", data)

except:
    screen_coords=[[0,0],
                 [0,1080],
                 [1920,0],
                 [1920,1080]]
    pool_coords = screen_coords
    detected_coords = l_point_test
    
CAM_NUMBER = 2 #default
try:
    with open("home/config.json", "r") as f:
        config = json.load(f)
        if ("camera" in config and "number" in config["camera"]):
            CAM_NUMBER = config["camera"]["number"]
except:
    print("No config file found, using default camera number")


############### Configuration Fenetre ###############
cv2.namedWindow("Billard", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Billard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


############### Configuration Caméra ###############


def get_frame():

    global camera_number
    cap = cv2.VideoCapture(CAM_NUMBER)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    ok, frame = cap.read()

    cap.release()
    
    if not ok:
        cv2.destroyAllWindows()
        print("Pas de Caméra detectée")
        input()
        exit()
    
    return frame

############### Events ###############

def draw_circle(event,x,y,flags,param):
    
    global l_circle, background
    
    if event in [cv2.EVENT_RBUTTONDOWN, cv2.EVENT_LBUTTONDOWN]:
        
        if len(l_circle)>=4:
            l_circle[min(enumerate([(xC-x)**2+(yC-y)**2 for xC,yC in l_circle]), key=lambda x: x[1])[0]]=[x,y]
        else:
            l_circle+=[[x,y]]
        
        frame=background.copy()
        
        for i,p1 in enumerate(l_circle):
            p1=tuple(p1)
            for p2 in l_circle[i+1:]:
                p2=tuple(p2)
                cv2.line(frame,p1,p2,(255,0,0),3)
            cv2.circle(frame,p1,20,(0,0,255),-1)
        
        cv2.imshow('Billard',frame)


############### Calibration Caméra ###############

background=get_frame()

cv2.putText(background,
            "Cliquez sur les 4 coins du billard !",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)

l_circle=pool_coords
cv2.imshow('Billard', background)

cv2.setMouseCallback('Billard', draw_circle)

frame=background.copy()
for i,p1 in enumerate(l_circle):
    p1=tuple(p1)
    for p2 in l_circle[i+1:]:
        p2=tuple(p2)
        cv2.line(frame,p1,p2,(255,0,0),3)
    cv2.circle(frame,p1,20,(0,0,255),-1)

cv2.imshow('Billard',frame)

cv2.waitKey(0)
while len(l_circle)<4:
    cv2.waitKey(0)
    
cv2.setMouseCallback('Billard', lambda *args: None)
    
pool_coords=l_circle.copy()

frame_camera=background.copy()


############### Calibration Projecteur ###############


calibration_test=np.zeros((1080,1920,3), np.uint8)

l_point_test = [[450,600],[450,850],[1250,600],[1230,850]]
#l_point_test = [[400,300],[400,780],[1520,300],[1520,780]] #Original test coords

# margeX=400
# margeY=300
# l_point_test=[]
# for x in [margeX, 1920-margeX]:
#     for y in [margeY, 1080-margeY]:
#         l_point_test += [[x,y]]
#         #cv2.circle(calibration_test,(x,y),40,(255,255,255),-1)


for i,p1 in enumerate(l_point_test):
    p1=tuple(p1)
    for p2 in l_point_test[i+1:]:
        p2=tuple(p2)
        cv2.line(calibration_test,p1,p2,(255,255,255),3)
    cv2.circle(calibration_test,p1,40,(255,255,255),-1)


cv2.imshow('Billard',calibration_test)
cv2.waitKey(80)

background=get_frame()

cv2.putText(background,
            "Cliquez gauche sur les 4 ronds projete sur le billard !",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)

for x,y in pool_coords:
    cv2.circle(background, (x,y), 20, (0,0,255), -1)

l_circle=detected_coords
cv2.imshow('Billard',background)

cv2.setMouseCallback('Billard',draw_circle)

frame=background.copy()
for i,p1 in enumerate(l_circle):
    p1=tuple(p1)
    for p2 in l_circle[i+1:]:
        p2=tuple(p2)
        cv2.line(frame,p1,p2,(255,0,0),3)
    cv2.circle(frame,p1,20,(0,0,255),-1)

cv2.imshow('Billard',frame)

cv2.waitKey(0)
while len(l_circle)<4:
    cv2.waitKey(0)

cv2.setMouseCallback('Billard', lambda *args: None)
    
detected_coords=l_circle.copy()

frame_projector = background.copy()
for p1 in detected_coords:
    cv2.circle(frame_projector, tuple(p1), 40, (0, 0, 255), -1)


############### Screen ###############

screen_coords=[[0,0],
                 [0,1080],
                 [1920,0],
                 [1920,1080]]


############### Informations ###############

def ordering(l_point1, l_point2):

    global background
    
    l_distance_ordered=[]
    for l_ordering in permutations(list(range(len(l_point1)))):
        d=0
        l_ordered_point=[]
        for i1,i2 in enumerate(l_ordering):
            d+=np.linalg.norm(np.array(l_point1[i1])
                              - np.array(l_point2[i2]))
            l_ordered_point+=[l_point2[i2]]
        
        l_distance_ordered+=[[d,l_ordered_point]]

    l_ordered_point=min(l_distance_ordered, key=lambda x: x[0])[1]

    frame=background.copy()
    
    for p1,p2 in zip(l_point1, l_ordered_point):
        p1=tuple(p1)
        p2=tuple(p2)
        cv2.line(frame,p1,p2,(255,0,0),3)
        cv2.circle(frame,p1,20,(0,0,255),-1)
        cv2.circle(frame,p2,20,(0,255,0),-1)

    cv2.imshow('Billard',frame)
    cv2.waitKey(2000)
    
    return l_ordered_point

#Ordering
pool_coords = ordering(detected_coords, pool_coords)
screen_coords = ordering(pool_coords, screen_coords)
l_point_test =  ordering(pool_coords, l_point_test)


detected_coords=np.float32(detected_coords)
pool_coords=np.float32(pool_coords)
screen_coords=np.float32(screen_coords)
projected_coords=np.float32(l_point_test)

# print("detected_coords : ",detected_coords)
# print("pool_coords    : ",pool_coords)
# print("screen_coords    : ",screen_coords)
# print("projected_coords      : ",projected_coords)

calibration_test2=np.zeros((1080,1920,3), np.uint8)
for i,p1 in enumerate(screen_coords):
    p1=tuple(map(int, p1))
    for p2 in screen_coords[i+1:]:
        p2=tuple(map(int, p2))
        cv2.line(calibration_test2,p1,p2,(255,255,255),3)
    cv2.circle(calibration_test2,p1,40,(255,255,255),-1)


cv2.putText(calibration_test2,
            "Image 2D a deformer dans un espace 3D pour fitter le billard, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Billard', calibration_test2)
cv2.waitKey(0)

tMat1_0 = cv2.getPerspectiveTransform(screen_coords, projected_coords)
tMat1_1 = cv2.getPerspectiveTransform(detected_coords, projected_coords)
tMat1_2 = cv2.getPerspectiveTransform(projected_coords, pool_coords)

projection_matrix = tMat1_1.dot(tMat1_2).dot(tMat1_0)

# print("tMat1_0 = cv2.getPerspectiveTransform(screen_coords, projected_coords)")
# print(">> %s\n" % tMat1_0)
# print("tMat1_1 = cv2.getPerspectiveTransform(detected_coords, projected_coords)")
# print(">> %s\n" % tMat1_1)
# print("tMat1_2 = cv2.getPerspectiveTransform(projected_coords, pool_coords)")
# print(">> %s\n" % tMat1_2)

# print("tMat1 = tMat1_1.dot(tMat1_2).dot(tMat1_0)")
# print(">> tMat1 (m_projector2camera) : ", projection_matrix)

test_1 = cv2.warpPerspective(calibration_test2, projection_matrix, (1920,1080), flags=cv2.INTER_LINEAR)
cv2.putText(test_1,
            "Image 2D deforme dans un espace 3D, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Billard',test_1)
cv2.waitKey(0)



poolFocus_matrix = cv2.getPerspectiveTransform(pool_coords, screen_coords)
# print("tMat2 (m_camera2screen) : ", poolFocus_matrix)
test_2 = cv2.warpPerspective(frame_camera, poolFocus_matrix, (1920,1080), flags=cv2.INTER_LINEAR)
cv2.putText(test_2,
            "Image 3D du billard déformer pour passer dans l'espace 2D de l'écran, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Billard',test_2)
# cv2.waitKey(0)

outpts = []
for x,y in screen_coords:
    x = (projection_matrix[0][0] * x + projection_matrix[0][1] * y + projection_matrix[0][2]) / (projection_matrix[2][0] * x + projection_matrix[2][1] * y + projection_matrix[2][2])
    y = (projection_matrix[1][0] * x + projection_matrix[1][1] * y + projection_matrix[1][2]) / (projection_matrix[2][0] * x + projection_matrix[2][1] * y + projection_matrix[2][2])
    x -= 960
    y -= 540
    x = (camera_distortion[0][0] * x + camera_distortion[0][1] * y + camera_distortion[0][2]) / (camera_distortion[2][0] * x + camera_distortion[2][1] * y + camera_distortion[2][2])
    y = (camera_distortion[1][0] * x + camera_distortion[1][1] * y + camera_distortion[1][2]) / (camera_distortion[2][0] * x + camera_distortion[2][1] * y + camera_distortion[2][2])
    outpts.append([int(x),int(y)])
outpts = np.float32(outpts)

d_information={"projection_matrix": projection_matrix,
               "poolFocus_matrix": poolFocus_matrix,
               "detected_coords": detected_coords.astype('int'),
               "pool_coords": pool_coords.astype('int'),
               "screen_coords": screen_coords.astype('int'),
               "projected_coords": projected_coords.astype('int'),
               "camera_distortion": camera_distortion,
               "outpts": outpts
        }
"""
with open('data.pkl', 'wb') as f:
    pickle.dump(d_information, f)
"""

d_information={k:v.tolist() for k,v in d_information.items()}

with open('home/calibration_data.json', 'w') as f:
    json.dump(d_information, f, indent=4)

print("Calibration terminée avec succès!")

cv2.destroyAllWindows()
exit()