import os
import time

import cv2
import numpy as np
import torch
import torch.nn as nn

from nets.face_detect import RetinaFace
from nets.nnutils.anchors import Anchors
from config import cfg_mnet, cfg_re50,model_args
from nets.nnutils.utils import letterbox_image, preprocess_input
from nets.nnutils.utils_bbox import (decode, decode_landm, non_max_suppression,
                              retinaface_correct_boxes)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


# ------------------------------------#
#   请注意主干网络与预训练权重的对应
#   即注意修改model_path和backbone
# ------------------------------------#
class Retinaface:
    @classmethod
    def get_defaults(cls, n):
        if n in model_args:
            return model_args[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    # ---------------------------------------------------#
    #   初始化Retinaface
    # ---------------------------------------------------#
    def __init__(self, **kwargs):
        self.cuda = torch.cuda.is_available()
        self.__dict__.update(model_args)
        for name, value in kwargs.items():
            setattr(self, name, value)

        # ---------------------------------------------------#
        #   不同主干网络的config信息
        # ---------------------------------------------------#
        if self.backbone == "mobilenet":
            self.cfg = cfg_mnet
        else:
            self.cfg = cfg_re50

        # ---------------------------------------------------#
        #   先验框的生成
        # ---------------------------------------------------#
        if self.letterbox_image:
            self.anchors = Anchors(self.cfg, image_size=[self.input_shape[0], self.input_shape[1]]).get_anchors()
        self.generate()

    # ---------------------------------------------------#
    #   载入模型
    # ---------------------------------------------------#
    def generate(self):
        # -------------------------------#
        #   载入模型与权值
        # -------------------------------#
        self.net = RetinaFace(cfg=self.cfg, mode='eval').eval()

        device = torch.device('cuda' if self.cuda else 'cpu')
        self.net.load_state_dict(torch.load(self.model_path, map_location=device))
        self.net = self.net.eval()
        print('{} model, and classes loaded.'.format(self.model_path))

        if self.cuda:
            self.net = nn.DataParallel(self.net).cuda()

    #   检测图片（With Cutt）
    def detect_image_return_flist(self, image):
        #   对输入图像进行一个备份，后面用于绘图
        old_image = image.copy()
        image = np.array(image)
        im_height, im_width, _ = np.shape(image)
        #   计算scale，用于将获得的预测框转换成原图的高宽
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        if self.letterbox_image:
            image = letterbox_image(image, [self.input_shape[1], self.input_shape[0]])
        else:
            self.anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        with torch.no_grad():
            #   图片预处理，归一化。
            image = torch.from_numpy(preprocess_input(image).transpose(2, 0, 1)).unsqueeze(0).type(torch.FloatTensor)

            if self.cuda:
                self.anchors = self.anchors.cuda()
                image = image.cuda()

            #   传入网络进行预测
            loc, conf, landms = self.net(image)

            #   对预测框进行解码
            boxes = decode(loc.data.squeeze(0), self.anchors, self.cfg['variance'])
            #   获得预测结果的置信度
            conf = conf.data.squeeze(0)[:, 1:2]
            #   对人脸关键点进行解码
            landms = decode_landm(landms.data.squeeze(0), self.anchors, self.cfg['variance'])

            #   对人脸识别结果进行堆叠
            boxes_conf_landms = torch.cat([boxes, conf, landms], -1)
            boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)

            if len(boxes_conf_landms) <= 0:
                return old_image, [], [], []

            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            if self.letterbox_image:
                boxes_conf_landms = retinaface_correct_boxes(boxes_conf_landms, \
                                                             np.array([self.input_shape[0], self.input_shape[1]]),
                                                             np.array([im_height, im_width]))

        boxes_conf_landms[:, :4] = boxes_conf_landms[:, :4] * scale
        boxes_conf_landms[:, 5:] = boxes_conf_landms[:, 5:] * scale_for_landmarks

        face_list = []
        score = []
        for b in boxes_conf_landms:
            score.append(b[4])
            b = list(map(int, b))
            b = [max(1, bi) for bi in b]  # bi可能为负数
            #
            face_list.append(old_image[b[1] + 5:b[3] - 5, b[0]:b[2]])  # 提取人脸
            # # cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)     # 右眼
            # # cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)   # 左眼
            # # cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)  # 鼻子
            # # cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)   # 嘴右
            # # cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)   # 嘴左
            # kp = [[b[5], b[6]], [b[7], b[8]], [b[9], b[10]], [b[11], b[12]], [b[13], b[14]]]
            # key_points.append(kp)
        return old_image, face_list, score,boxes_conf_landms

    # ---------------------------------------------------#
    #   检测图片(返回单张)
    # ---------------------------------------------------#
    def detect_image(self, image):
        # ---------------------------------------------------#
        #   对输入图像进行一个备份，后面用于绘图
        # ---------------------------------------------------#
        old_image = image.copy()
        # ---------------------------------------------------#
        #   把图像转换成numpy的形式
        # ---------------------------------------------------#
        image = np.array(image, np.float32)
        # ---------------------------------------------------#
        #   计算输入图片的高和宽
        # ---------------------------------------------------#
        im_height, im_width, _ = np.shape(image)
        # ---------------------------------------------------#
        #   计算scale，用于将获得的预测框转换成原图的高宽
        # ---------------------------------------------------#
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        # ---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        # ---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image, [self.input_shape[1], self.input_shape[0]])
        else:
            self.anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        with torch.no_grad():
            # -----------------------------------------------------------#
            #   图片预处理，归一化。
            # -----------------------------------------------------------#
            image = torch.from_numpy(preprocess_input(image).transpose(2, 0, 1)).unsqueeze(0).type(torch.FloatTensor)

            if self.cuda:
                self.anchors = self.anchors.cuda()
                image = image.cuda()

            # ---------------------------------------------------------#
            #   传入网络进行预测
            # ---------------------------------------------------------#
            loc, conf, landms = self.net(image)

            # -----------------------------------------------------------#
            #   对预测框进行解码
            # -----------------------------------------------------------#
            boxes = decode(loc.data.squeeze(0), self.anchors, self.cfg['variance'])
            # -----------------------------------------------------------#
            #   获得预测结果的置信度
            # -----------------------------------------------------------#
            conf = conf.data.squeeze(0)[:, 1:2]
            # -----------------------------------------------------------#
            #   对人脸关键点进行解码
            # -----------------------------------------------------------#
            landms = decode_landm(landms.data.squeeze(0), self.anchors, self.cfg['variance'])

            # -----------------------------------------------------------#
            #   对人脸识别结果进行堆叠
            # -----------------------------------------------------------#
            boxes_conf_landms = torch.cat([boxes, conf, landms], -1)
            boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)

            if len(boxes_conf_landms) <= 0:
                return old_image

            # ---------------------------------------------------------#
            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            # ---------------------------------------------------------#
            if self.letterbox_image:
                boxes_conf_landms = retinaface_correct_boxes(boxes_conf_landms,
                                                             np.array([self.input_shape[0], self.input_shape[1]]),
                                                             np.array([im_height, im_width]))

        boxes_conf_landms[:, :4] = boxes_conf_landms[:, :4] * scale
        boxes_conf_landms[:, 5:] = boxes_conf_landms[:, 5:] * scale_for_landmarks

        for b in boxes_conf_landms:
            text = "{:.4f}".format(b[4])
            b = list(map(int, b))
            # ---------------------------------------------------#
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分
            # ---------------------------------------------------#
            cv2.rectangle(old_image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(old_image, text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            print(b[0], b[1], b[2], b[3], b[4])
            # ---------------------------------------------------#
            #   b[5]-b[14]为人脸关键点的坐标
            # ---------------------------------------------------#
            cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)
        return old_image

    def get_FPS(self, image, test_interval):
        # ---------------------------------------------------#
        #   把图像转换成numpy的形式
        # ---------------------------------------------------#
        image = np.array(image, np.float32)
        # ---------------------------------------------------#
        #   计算输入图片的高和宽
        # ---------------------------------------------------#
        im_height, im_width, _ = np.shape(image)

        # ---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        # ---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image, [self.input_shape[1], self.input_shape[0]])
        else:
            self.anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        with torch.no_grad():
            # -----------------------------------------------------------#
            #   图片预处理，归一化。
            # -----------------------------------------------------------#
            image = torch.from_numpy(preprocess_input(image).transpose(2, 0, 1)).unsqueeze(0).type(torch.FloatTensor)

            if self.cuda:
                self.anchors = self.anchors.cuda()
                image = image.cuda()

            # ---------------------------------------------------------#
            #   传入网络进行预测
            # ---------------------------------------------------------#
            loc, conf, landms = self.net(image)
            # -----------------------------------------------------------#
            #   对预测框进行解码
            # -----------------------------------------------------------#
            boxes = decode(loc.data.squeeze(0), self.anchors, self.cfg['variance'])
            # -----------------------------------------------------------#
            #   获得预测结果的置信度
            # -----------------------------------------------------------#
            conf = conf.data.squeeze(0)[:, 1:2]
            # -----------------------------------------------------------#
            #   对人脸关键点进行解码
            # -----------------------------------------------------------#
            landms = decode_landm(landms.data.squeeze(0), self.anchors, self.cfg['variance'])

            # -----------------------------------------------------------#
            #   对人脸识别结果进行堆叠
            # -----------------------------------------------------------#
            boxes_conf_landms = torch.cat([boxes, conf, landms], -1)
            boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)

        t1 = time.time()
        for _ in range(test_interval):
            with torch.no_grad():
                # ---------------------------------------------------------#
                #   传入网络进行预测
                # ---------------------------------------------------------#
                loc, conf, landms = self.net(image)
                # -----------------------------------------------------------#
                #   对预测框进行解码
                # -----------------------------------------------------------#
                boxes = decode(loc.data.squeeze(0), self.anchors, self.cfg['variance'])
                # -----------------------------------------------------------#
                #   获得预测结果的置信度
                # -----------------------------------------------------------#
                conf = conf.data.squeeze(0)[:, 1:2]
                # -----------------------------------------------------------#
                #   对人脸关键点进行解码
                # -----------------------------------------------------------#
                landms = decode_landm(landms.data.squeeze(0), self.anchors, self.cfg['variance'])

                # -----------------------------------------------------------#
                #   对人脸识别结果进行堆叠
                # -----------------------------------------------------------#
                boxes_conf_landms = torch.cat([boxes, conf, landms], -1)
                boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)

        t2 = time.time()
        tact_time = (t2 - t1) / test_interval
        return tact_time

    # ---------------------------------------------------#
    #   检测图片
    # ---------------------------------------------------#
    def get_map_txt(self, image):
        # ---------------------------------------------------#
        #   把图像转换成numpy的形式
        # ---------------------------------------------------#
        image = np.array(image, np.float32)
        # ---------------------------------------------------#
        #   计算输入图片的高和宽
        # ---------------------------------------------------#
        im_height, im_width, _ = np.shape(image)
        # ---------------------------------------------------#
        #   计算scale，用于将获得的预测框转换成原图的高宽
        # ---------------------------------------------------#
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        # ---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        # ---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image, [self.input_shape[1], self.input_shape[0]])
        else:
            self.anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        with torch.no_grad():
            # -----------------------------------------------------------#
            #   图片预处理，归一化。
            # -----------------------------------------------------------#
            image = torch.from_numpy(preprocess_input(image).transpose(2, 0, 1)).unsqueeze(0).type(torch.FloatTensor)

            if self.cuda:
                self.anchors = self.anchors.cuda()
                image = image.cuda()

            # ---------------------------------------------------------#
            #   传入网络进行预测
            # ---------------------------------------------------------#
            loc, conf, landms = self.net(image)
            # -----------------------------------------------------------#
            #   对预测框进行解码
            # -----------------------------------------------------------#
            boxes = decode(loc.data.squeeze(0), self.anchors, self.cfg['variance'])
            # -----------------------------------------------------------#
            #   获得预测结果的置信度
            # -----------------------------------------------------------#
            conf = conf.data.squeeze(0)[:, 1:2]
            # -----------------------------------------------------------#
            #   对人脸关键点进行解码
            # -----------------------------------------------------------#
            landms = decode_landm(landms.data.squeeze(0), self.anchors, self.cfg['variance'])

            # -----------------------------------------------------------#
            #   对人脸识别结果进行堆叠
            # -----------------------------------------------------------#
            boxes_conf_landms = non_max_suppression(torch.cat([boxes, conf, landms], -1), self.confidence)

            if len(boxes_conf_landms) <= 0:
                return np.array([])

            # ---------------------------------------------------------#
            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            # ---------------------------------------------------------#
            if self.letterbox_image:
                boxes_conf_landms = retinaface_correct_boxes(boxes_conf_landms,
                                                             np.array([self.input_shape[0], self.input_shape[1]]),
                                                             np.array([im_height, im_width]))

        boxes_conf_landms[:, :4] = boxes_conf_landms[:, :4] * scale
        boxes_conf_landms[:, 5:] = boxes_conf_landms[:, 5:] * scale_for_landmarks

        return boxes_conf_landms
