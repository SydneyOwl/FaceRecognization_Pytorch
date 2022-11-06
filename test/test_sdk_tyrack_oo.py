import numpy as np
import torch
from utils.videoutil import cutToFit
from nets.emotion import ResNet18_ARM___RAF
import cv2
from nets.retinaface import Retinaface
from utils import facesdk

from PIL import Image
MONITOR_STREAM = "rtmp://YOUR_IP:1935/live/test"

cudahere = torch.cuda.is_available()
retinaface = Retinaface()
model = ResNet18_ARM___RAF().cuda() if cudahere else ResNet18_ARM___RAF()
checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cuda') if cudahere else torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cpu')
model.load_state_dict(checkpoint["model_state_dict"], strict=False)
source = cv2.imread("./test.jpg")
# cap = cv2.VideoCapture(MONITOR_STREAM)
recoginzed_face = []
face_detail = {}
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
source = cv2.resize(source, (source.shape[1]//4*4, source.shape[0]))
frame = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(frame)
facepos_dict = {}
if face_list != []:
    fNum = 0
    for v in boxes_conf_landms:
        facepos_dict[fNum] = [v[0],v[1],v[2],v[3]]
        fNum+=1
print(facepos_dict)
#         # print(face_list)
# #     # print(facesdk.getFacePos(image))
    # print(facesdk.discoverNewFace(_bak,recoginzed_face,face_detail,facepos_dict))
# res, detectedFaces = facesdk.face_engine.ASFDetectFaces(cv2.imread("./test.jpg"))
# print(detectedFaces)
ans = facesdk.discoverNewFace(source,recoginzed_face,face_detail,facepos_dict)
print(ans)