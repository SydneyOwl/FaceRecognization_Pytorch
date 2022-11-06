import cv2
import numpy as np
import socketio
sio = socketio.Client()
cap = cv2.VideoCapture(0)
is_server_accepting = False
def sendPic():
    while cap.isOpened():
        success, image = cap.read()
        image_numpy = np.array(image)
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        if not sio.connected:
            cv2.putText(image_numpy,"Connecting to server...",(10, 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))
            cv2.imshow("FerServer_Client", image)
        else:
            image_numpy = np.array(image)
            _, im = cv2.imencode('.jpg', image_numpy)
            try:
                sio.emit("camdata",im.tobytes(),namespace="/wss/cam")
            except Exception as e:
                print(repr(e))
                break
            cv2.imshow("FerServer_Client", image_numpy)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()

@sio.on('connect',namespace = '/wss/cam')
def on_connect():
    sendPic()
sio.connect('wss://fc.mrchrist.site:60089/',namespaces="/wss/cam")
sio.wait()