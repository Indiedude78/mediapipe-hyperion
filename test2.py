# Start capturing video from webcam
import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
# send json requests to an API endpoint
# import necessary modules
import requests
import json

cap = cv2.VideoCapture(0)

# Initializing the Model
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
mpDrawStyles = mp.solutions.drawing_styles
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=1)

# define the endpoint
endpoint = "http://192.168.1.117:8090/json-rpc"

# define the headers
headers = {'Content-Type': 'application/json',
           'Accept': 'application/json'}

while True:

    # Read video frame by frame
    success, img = cap.read()

    # Flip the image(frame)
    img = cv2.flip(img, 1)

    # Convert BGR image to RGB image
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the RGB image
    results = hands.process(imgRGB)

    # If hands are present in image(frame)
    if results.multi_hand_landmarks:

        # Both Hands are present in image(frame)
        if len(results.multi_handedness) == 2:
            # Display 'Both Hands' on the image
            cv2.putText(img, 'Both Hands', (250, 50),
                        cv2.FONT_HERSHEY_COMPLEX, 0.9,
                        (0, 255, 0), 2)

        # If any hand present
        else:
            for i in results.multi_handedness:

                # Return whether it is Right or Left Hand
                label = MessageToDict(i)[
                    'classification'][0]['label']

                if label == 'Left':

                    # Display 'Left Hand' on left side of window
                    cv2.putText(img, label+' Hand', (20, 50),
                                cv2.FONT_HERSHEY_COMPLEX, 0.9,
                                (0, 255, 0), 2)
                    # draw landmarks on left hand
                    mpDraw.draw_landmarks(
                        img,
                        results.multi_hand_landmarks[0],
                        mpHands.HAND_CONNECTIONS,
                        mpDrawStyles.get_default_hand_landmarks_style(),
                        mpDrawStyles.get_default_hand_connections_style())
                    tips = [0, 4, 8, 12, 16, 20]
                    # get the tip of the index finger
                    
                    data = {
                        "command": "componentstate",
                        "componentstate":
                        {
                            "component": "LEDDEVICE",
                            "state": True
                        }
                    }
                    # send the request
                    response = requests.post(
                        endpoint, data=json.dumps(data), headers=headers)
                    # print the response
                    # print(response.text)
                    # converrt the response text to a dictionary
                    response_dict = json.loads(response.text)
                    # print the success key of the dictionary
                    print(response_dict['success'])

                if label == 'Right':

                    # Display 'Left Hand' on left side of window
                    cv2.putText(img, label+' Hand', (460, 50),
                                cv2.FONT_HERSHEY_COMPLEX,
                                0.9, (0, 255, 0), 2)
                    data = {
                        "command": "componentstate",
                        "componentstate":
                        {
                            "component": "LEDDEVICE",
                            "state": False
                        }
                    }
                    # send the request
                    response = requests.post(
                        endpoint, data=json.dumps(data), headers=headers)
                    # print the response
                   # print(response.text)
                    # convert the response text to a dictionary
                    response_dict = json.loads(response.text)
                    # print success key of the dictionary
                    print(response_dict['success'])

    # Display Video and when 'q' is entered, destroy the window
    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
