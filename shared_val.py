import queue
import threading

tmp_face = []
lock = threading.RLock()
frame_queue = queue.Queue(-1)
# newface_queue = queue.Queue(-1)
_is_cam_available = False
monitorFrameInfo = {}
monitorFrameInfo["faceCountInThisFrame"]=0
monitorFrameInfo["emoInfoPerFrame"]={}
monitorFrameInfo["emoInfoTotal"]={}
monitorFrameInfo["width"]=0
monitorFrameInfo["height"]=0