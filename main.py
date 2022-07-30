from email import header
import time
import cv2
import mediapipe as mp
import numpy as np
import requests
import json

# define the endpoint
endpoint = "http://192.168.1.117:8090/json-rpc"

# define the headers
headers = {'Content-Type': 'application/json',
           'Accept': 'application/json'}


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
# make cv2 window bigger
cv2.namedWindow("preview", cv2.WINDOW_NORMAL)


def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=20):
    dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
    pts = []
    for i in np.arange(0, dist, gap):
        r = i / dist
        x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
        y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
        p = (x, y)
        pts.append(p)
        if style == 'dotted':
            for p in pts:
                cv2.circle(img, p, thickness, color, -1)
        else:
            s = pts[0]
            e = pts[0]
            i = 0
            for p in pts:
                s = e
                e = p
                if i % 2 == 1:
                    cv2.line(img, s, e, color, thickness)
                i += 1


with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=2) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image.shape
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    lmList.append([id, x, y])
                    # print(lmList)
                    tips = [0, 4, 8, 12, 16, 20]
                    for id in tips:
                        cv2.circle(image, (x, y), 5,
                                   (255, 255, 255), cv2.FILLED)
                # mp_drawing.draw_landmarks(
                #     image,
                #     hand_landmarks,
                #     mp_hands.HAND_CONNECTIONS)
                if (lmList[4][1] > lmList[3][1] and lmList[8][1] > lmList[6][1] and lmList[12][1] < lmList[10][1] and lmList[16][1] < lmList[14][1] and lmList[20][1] < lmList[18][1]):
                    print("thumb up")
                    drawline(image, (lmList[4][1], lmList[4][2]), (lmList[8]
                                                                   [1], lmList[8][2]), (0, 0, 0), 2, 'dotted', 10)
                    # calculate the distance between the tips of index and thumb
                    dist = int(((lmList[4][1] - lmList[8][1]) ** 2 +
                                (lmList[4][2] - lmList[8][2]) ** 2) ** .5)
                    # print(dist)
                    max_distance = 200
                    dist_percentage = int((dist / max_distance) * 100)
                    if dist_percentage > 100:
                        dist_percentage = 100
                    print(dist_percentage)
                    # send the request
                    data = {
                        "command": "adjustment",
                        "adjustment":
                        {
                            "classic_config": False,
                            "brightness": dist_percentage
                        }
                    }
                    response = requests.post(
                        endpoint, data=json.dumps(data), headers=headers)
                    print(response.text)
                elif (lmList[8][2] < lmList[6][2] and lmList[12][2] < lmList[10][2] and lmList[16][2] > lmList[14][2] and lmList[20][2] > lmList[18][2]):
                    print("peace sign")
                    data = {
                        "command": "componentstate",
                        "componentstate":
                        {
                            "component": "LEDDEVICE",
                            "state": True
                        }
                    }
                    response = requests.post(
                        endpoint, data=json.dumps(data), headers=headers)
                    print("Light turned on")
                    time.sleep(2)
                elif (lmList[12][2] < lmList[10][2] and lmList[16][2] > lmList[14][2] and lmList[20][2] > lmList[18][2] and lmList[8][2] > lmList[6][2]):

                    print("fuck off sign")
                    data = {
                        "command": "componentstate",
                        "componentstate":
                        {
                            "component": "LEDDEVICE",
                            "state": False
                        }
                    }
                    response = requests.post(
                        endpoint, data=json.dumps(data), headers=headers)
                    print("Light turned off")
                    time.sleep(2)
                # check if the hand is open
                elif (lmList[4][1] > lmList[3][1] and lmList[8][2] < lmList[6][2] and lmList[12][2] < lmList[10][2] and lmList[16][2] < lmList[14][2] and lmList[20][2] < lmList[18][2]):
                    print("hand is open")
                    time.sleep(5)
                    # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        # get fps
        fps = cap.get(cv2.CAP_PROP_FPS)
        # print("fps: ", fps)
        if cv2.waitKey(5) & 0xFF == 27:
            break
        # if q is pressed, close the window
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
