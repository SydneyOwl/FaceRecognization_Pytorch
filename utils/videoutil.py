import os
import cv2
from app import PROCESSED_FOLDER
from PIL import Image

from nets.nnutils.img_tools import addSquare,preprocess
from . import retinaface,model,cudahere,emoLabel
import torch
def cutToFit(frame,width,height):
    img = cv2.resize(frame, (width//4*4, height))
    return img
def processVideo(path):
    cap = cv2.VideoCapture(path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # form = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # size = (width,height)
    # 视频对象的输出
    cur = 0
    _,orgFile = os.path.split(path)
    output = cv2.VideoWriter(
        PROCESSED_FOLDER+'/processed-' + orgFile, fourcc, fps, (width, height))
    face_info_total_sum = [0, 0, 0, 0, 0, 0, 0]  # 总计人脸数据
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        _bak = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        fCount = 0  # 单帧人脸计数
        face_info_per_frame = [0, 0, 0, 0, 0, 0, 0]  # 每帧的人脸数据
        # 进行检测
        oldimage, face_list, score, boxes_conf_landms = retinaface.detect_image_return_flist(
            frame)
        if face_list != []:
            emo_list = []
            for i, f in enumerate(face_list):
                try:
                    img = Image.fromarray(f)
                    image = preprocess(img)
                    outputs, _ = model(
                        image.cuda()) if cudahere else model(image)
                    _, predicts = torch.max(outputs, 1)
                    emo_list.append(
                        emoLabel[predicts])
                    face_info_per_frame[predicts] += 1
                    face_info_total_sum[predicts] += 1
                    fCount += 1
                except Exception as e:
                    print(repr(e))
                    continue
            addSquare(_bak, boxes_conf_landms, emo_list)
        output.write(_bak)
        cv2.putText(_bak, str("processing..  {:.3f}%".format((cur / total_frame)*10*10)), (30, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))
        _, im = cv2.imencode(
            '.jpg', _bak, [cv2.IMWRITE_JPEG_QUALITY, 40])  # compress!!!!
        cur += 1
        yield (im.tobytes(), (cur / total_frame)*100, fCount, face_info_per_frame, face_info_total_sum, width, height)


def processImageNumpy(img_arr, face_info_total_sum):
    # nonlocal face_info_total_sum
    _bak = img_arr
    frame = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    fCount = 0  # 单帧人脸计数
    face_info_per_frame = [0, 0, 0, 0, 0, 0, 0]  # 每帧的人脸数据
    # 进行检测
    _, face_list, _, boxes_conf_landms = retinaface.detect_image_return_flist(
        frame)
    if face_list != []:
        # # print(len(face_list))
        emo_list = []
        for i, f in enumerate(face_list):
            try:
                img = Image.fromarray(f)
                image = preprocess(img)
                outputs, _ = model(
                    image.cuda()) if cudahere else model(image)
                _, predicts = torch.max(outputs, 1)
                emo_list.append(
                    emoLabel[predicts])
                face_info_per_frame[predicts] += 1
                face_info_total_sum[predicts] += 1
                fCount += 1
            except Exception as e:
                print(repr(e))
                continue
        addSquare(_bak, boxes_conf_landms, emo_list)
    # _, im = cv2.imencode('.jpg', _bak)
    return (_bak.tostring(), fCount, face_info_per_frame,boxes_conf_landms)
#检查位置偏移量是否过大
def checkPos(l1,l2,t1,t2,r1,r2,b1,b2):
    pass