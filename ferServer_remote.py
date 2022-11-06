import os
import time
import cv2
import numpy as np
import threading
from app import create_app, socketio,UPLOAD_FOLDER,PROCESSED_FOLDER,MONITOR_STREAM,emoLabel
import subprocess as sp
from utils.cmdutil import genCommand
from utils.videoutil import processImageNumpy
# from shared_val import frame_queue,_is_cam_available,monitorFrameInfo
import shared_val
from utils.facesdk import calcNewFaceInFrame
# app.config['SECRET_KEY'] = 'secret!'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

#推流
# frame_queue,_is_cam_available,monitorFrameInfo = shared_val.frame_queue,shared_val._is_cam_available,shared_val.monitorFrameInfo


def putImg():
    while True:
        while not shared_val._is_cam_available:
            time.sleep(0.5)
        cap = cv2.VideoCapture(MONITOR_STREAM)
        shared_val.monitorFrameInfo["width"]=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        shared_val.monitorFrameInfo["height"]=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # monitorFrameInfo["fps"]=int(cap.get(cv2.CAP_PROP_FPS))
        while True:
            if not shared_val._is_cam_available:
                print("queue shutdown!")
                while not shared_val.frame_queue.empty():
                    shared_val.frame_queue.get()
                break
            ret, frame = cap.read()
            if ret:
                shared_val.frame_queue.put(frame)
                shared_val.frame_queue.get() if shared_val.frame_queue.qsize() > 1 else time.sleep(0.01)

def watchCam() -> None:
    recognized_face = []
    frame_count = 0
    while True:
        # shared_val.lock.acquire()
        # while not shared_val.newface_queue.empty():
        #     shared_val.newface_queue.get()
        # shared_val.lock.release()
        while not shared_val._is_cam_available:
            # print("wait for cam...")
            time.sleep(1)
        shared_val.monitorFrameInfo["faceCountInThisFrame"]=0
        shared_val.monitorFrameInfo["emoInfoPerFrame"]={}
        shared_val.monitorFrameInfo["emoInfoTotal"]={}
        while shared_val.monitorFrameInfo["width"]==0:time.sleep(1)
        # print("read")
        face_info_total_sum = [0, 0, 0, 0, 0, 0, 0]  # init face
        cmd = genCommand(shared_val.monitorFrameInfo["width"],shared_val.monitorFrameInfo["height"])
        p = sp.Popen(cmd, stdin=sp.PIPE)
        while True:
            if shared_val.frame_queue.empty():
                if not shared_val._is_cam_available:
                    break
                else:
                    continue
            frame = shared_val.frame_queue.get()
            img_numpy = np.array(frame)
            try:
                img, faceCount, faceInfo, face_pos = processImageNumpy(
                    img_numpy, face_info_total_sum)
                frame_count+=1
                if frame_count == 20:
                    result = calcNewFaceInFrame(face_pos,frame,recognized_face)
                    # shared_val.newface_queue.put(result)
                    if result!={}:
                        for value in result.values():
                            shared_val.tmp_face.append(value)
                    frame_count=0
                shared_val.monitorFrameInfo["faceCountInThisFrame"]=faceCount
                shared_val.monitorFrameInfo["emoInfoPerFrame"]=dict(zip(emoLabel, faceInfo))
                shared_val.monitorFrameInfo["emoInfoTotal"]=dict(zip(emoLabel, face_info_total_sum))
                p.stdin.write(img)
            except Exception as e:
                print(e)



app = create_app(debug=True)
if __name__ == "__main__":
    watchProcess = threading.Thread(target=watchCam)
    watchProcess.start()
    putProcess = threading.Thread(target=putImg)
    putProcess.start()
    socketio.run(app,debug=False, port=1235,use_reloader=False,allow_unsafe_werkzeug=True)
