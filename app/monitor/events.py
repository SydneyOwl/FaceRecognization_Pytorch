import time

from .. import socketio
from flask_socketio import emit
import shared_val
@socketio.on('connect', namespace='/wss/realtimeCam')
def cemoInfo():
    pass

@socketio.on('json',namespace='/wss/realtimeCam')
def collectFace():
    """
    {
        "type":"capFace",
        "chg":True
    }
    """
    pass
@socketio.on('message', namespace='/wss/realtimeCam')
def emoInfo(message):
    while True:
        # shared_val.monitorFrameInfo["width"]=0
        while not shared_val._is_cam_available:
            emit('data', {
                    'type': 'videoFrame',
                    'status': 202,
                    'info':"ERR_CAM_NOT_AVAILABLE"
                })
            time.sleep(1)
        while shared_val.monitorFrameInfo["width"]==0:
            time.sleep(1)
        while shared_val._is_cam_available:
            # newface = {}
            # if not shared_val.newface_queue.empty():
            #     newface = shared_val.newface_queue.get(timeout=1)
            # else:newface={}
            # toNZX = []
            # for i in newface.values():
            #     toNZX.append(i)
            #     shared_val.tmp_face.append(i)
            emit('data', {
                    'type': 'videoFrame',
                    'status': 200,
                    # 'img': img,
                    'faceCountInThisFrame': shared_val.monitorFrameInfo["faceCountInThisFrame"],
                    'emoInfoPerFrame': shared_val.monitorFrameInfo["emoInfoPerFrame"],
                    "emoInfoTotal": shared_val.monitorFrameInfo["emoInfoTotal"],
                    "width": shared_val.monitorFrameInfo["width"],
                    "height": shared_val.monitorFrameInfo["height"],
                    # "newFace":str(toNZX)
                })
            # print(shared_val.tmp_face)
            time.sleep(1)
    
@socketio.on('disconnect', namespace='/wss/realtimeCam')
def demoInfo():
    pass