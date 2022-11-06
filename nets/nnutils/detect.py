import math
import os

import cv2
import numpy as np
from nets.retinaface import Retinaface

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def detect(image):
    retinaface = Retinaface()
    r_image, faces, kps, score = retinaface.detect_image(image)
    if len(faces) == 0:
        return [], []
    else:
        maxi = score.index(max(score))
        return faces[maxi], kps[maxi]


def face_alignment(face, kps):
    # 计算两眼的中心坐标
    eye_center = ((kps[0][0] + kps[1][0]) * 1. / 2, (kps[0][1] + kps[1][1]) * 1. / 2)
    dx = (kps[1][0] - kps[0][0])
    dy = (kps[1][1] - kps[0][1])
    # 计算角度
    angle = math.atan2(dy, dx) * 180. / math.pi
    # 计算仿射矩阵
    RotateMatrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1.5)
    # 进行仿射变换，即旋转
    faces_aligned = cv2.warpAffine(face, RotateMatrix, (face.shape[1], face.shape[0]), flags=cv2.INTER_AREA)

    return faces_aligned


def align(image):
    w = image.width
    h = image.height

    image = np.array(image)
    _, kps = detect(image)

    if len(kps) == 0:  # 关键点解析失败
        print('no face key points')
        return []

    face_aligned = face_alignment(image, kps)

    face_aligned = face_aligned[0:round(h * 0.8), round(w * 0.1):round(w * 0.9)]

    image, _ = detect(face_aligned)

    return image


def transformation_from_points(points1, points2):
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)
    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2
    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2
    U, S, Vt = np.linalg.svd(points1.T * points2)
    R = (U * Vt).T
    return np.vstack([np.hstack(((s2 / s1) * R, c2.T - (s2 / s1) * R * c1.T)), np.matrix([0., 0., 1.])])


def warp_im(img_im, orgi_landmarks, tar_landmarks):
    pts1 = np.float64(np.matrix([[point[0], point[1]] for point in orgi_landmarks]))
    pts2 = np.float64(np.matrix([[point[0], point[1]] for point in tar_landmarks]))
    M = transformation_from_points(pts1, pts2)
    dst = cv2.warpAffine(img_im, M[:2], (img_im.shape[1], img_im.shape[0]))
    return dst


def align2(img):
    imgSize = [100, 100]

    coord5point = [[30.2946, 51.6963],
                   [65.5318, 51.6963],
                   [48.0252, 71.7366],
                   [33.5493, 92.3655],
                   [62.7299, 92.3655]]

    img = np.array(img)
    _, kps = detect(img)

    if len(kps) == 0:  # 关键点解析失败
        print('no face key points')
        return []

    dst = warp_im(img, kps, coord5point)
    crop_im = dst[0:imgSize[0], 0:imgSize[1]]
    return crop_im
