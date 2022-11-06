# coding=utf-8
import os.path

from nets.emotion import ResNet18_ARM___RAF
import cv2
import numpy as np
from PIL import Image
import torch
from utils.img_tools import preprocess, addSquare
from nets.retinaface import Retinaface

video_keys = {}
cudahere = torch.cuda.is_available()
retinaface = Retinaface()
model = ResNet18_ARM___RAF().cuda() if cudahere else ResNet18_ARM___RAF()
checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cuda') if cudahere else torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cpu')
model.load_state_dict(checkpoint["model_state_dict"], strict=False)
def testLocal():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            break
        image_numpy = np.array(image)
        _bak = image_numpy
        frame = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2RGB)
        # 进行检测
        oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(frame)
        if face_list == []:
            cv2.imshow('rec', _bak)
        else:
            # # print(len(face_list))
            emo_list = []
            for i, f in enumerate(face_list):
                try:
                    img = Image.fromarray(f)
                    image = preprocess(img)
                    outputs, _ = model(image.cuda()) if cudahere else model(image)
                    _, predicts = torch.max(outputs, 1)
                    emo_list.append(['amaze', 'fear', 'disgust', 'happy', 'sad', 'anger', "neutral"][predicts])
                except Exception as e:
                    print(repr(e))
                    cv2.imshow("rec", _bak)
                    continue
            addSquare(_bak, boxes_conf_landms, emo_list)
            # cv2.imshow('MediaPipe FaceMesh', _bak)
            cv2.imshow("rec", _bak)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()


# testLocal()
def testDataset(pathFather):
    retinaface = Retinaface()
    model = ResNet18_ARM___RAF().cuda()
    checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth")
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    fl = ["angry", "neutral"]
    for i in fl:
        file = os.listdir(i)
        corr = 0
        err = 0
        for j in file:
            img = Image.open(os.path.join(i, j))
            image_numpy = np.array(img)
            frame = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2RGB)
            oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(frame)
            try:
                img = face_list[0]
            except IndexError:
                err+=1
                continue
            image = preprocess(img)
            outputs, _ = model(image.cuda())
            _, predicts = torch.max(outputs, 1)
            ans = ['amaze', 'fear', 'disgust', 'happy', 'sad', 'angry', "neutral"][predicts]
            if ans == i:
                corr += 1
        print((corr / (len(file)-err)) * 100)


# testLocal()
def videoRecognization(path):
    cap = cv2.VideoCapture(path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    form = int(cap.get(cv2.CAP_PROP_FOURCC))
    total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(width,height,fps,form,total_frame)
    # size = (width,height)
    #视频对象的输出
    cur = 0
    output = cv2.VideoWriter('video_output.mp4', form, fps, (width, height))
    # out = cv2.VideoWriter('out.avi', fourcc, 20.0, (width, height))
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        _bak = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 进行检测
        oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(frame)
        if face_list != []:
            # # print(len(face_list))
            emo_list = []
            for i, f in enumerate(face_list):
                try:
                    img = Image.fromarray(f)
                    image = preprocess(img)
                    outputs, _ = model(image.cuda()) if cudahere else model(image)
                    _, predicts = torch.max(outputs, 1)
                    emo_list.append(['amaze', 'fear', 'disgust', 'happy', 'sad', 'anger', "neutral"][predicts])
                except Exception as e:
                    print(repr(e))
                    continue
            addSquare(_bak, boxes_conf_landms, emo_list)
        output.write(_bak) #写入视频
        cur+=1
        print("Progress "+str((cur/total_frame)*100)+'% Done')
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release() #释放视频
    output.release()
    cv2.destroyAllWindows() #释放所有的显示窗口
# videoRecognization("D:\\UserData\\Doc\\Tencent Files\\2503657999\\FileRecv\\test.mp4")