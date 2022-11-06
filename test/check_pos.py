import numpy as np
import torch
from nets.emotion import ResNet18_ARM___RAF
import cv2
from nets.retinaface import Retinaface


cudahere = torch.cuda.is_available()
retinaface = Retinaface()
model = ResNet18_ARM___RAF().cuda() if cudahere else ResNet18_ARM___RAF()
checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cuda') if cudahere else torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cpu')
model.load_state_dict(checkpoint["model_state_dict"], strict=False)
image = cv2.imread("/home/ubuntu/Fer/lss/FR/asserts/1.jpg")
image_numpy = np.array(image)
frame = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2RGB)
# 进行检测
oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(frame)
print(boxes_conf_landms)