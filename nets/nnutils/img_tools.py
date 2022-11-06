import cv2
import numpy as np
from torchvision import transforms

color = {
    'amaze':(99,102,241),
    'fear':(30,58,138), 
    'disgust':(6,95,70), 
    'happy':(16,185,129), 
    'sad':(245,158,11), 
    'anger':(239,68,68),
    "neutral":(59,130,246)
}

def add_gaussian_noise(image_array, mean=0.0, var=30):
    std = var**0.5
    noisy_img = image_array + np.random.normal(mean, std, image_array.shape)
    noisy_img_clipped = np.clip(noisy_img, 0, 255).astype(np.uint8)
    return noisy_img_clipped

def flip_image(image_array):
    return cv2.flip(image_array, 1)

def color2gray(image_array):
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    gray_img_3d = image_array.copy()
    gray_img_3d[:, :, 0] = gray
    gray_img_3d[:, :, 1] = gray
    gray_img_3d[:, :, 2] = gray
    return gray_img_3d
def preprocess(img):
    """
    Pre-process an image to meet the size, type and format
    requirements specified by the parameters.
    """
    # np.set_printoptions(threshold='nan')

    #     if c == 1:
    #         sample_img = img.convert('L')
    #     else:
    #         sample_img = img.convert('RGB')

    # resized_img = sample_img.resize((w, h), Image.BILINEAR)
    # img = img.convert("RGB")
    img = transforms.ToTensor()(img)
    # img = img.transpose(2, 0, 1)
    tf = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    resized = tf(img).unsqueeze(0)
    return resized


def addSquare(old_image, boxes_conf_landms, emo):
    i = 0
    for b in boxes_conf_landms:
        col = color[emo[i]]
        text = "{:.4f}".format(b[4])
        b = list(map(int, b))
        # ---------------------------------------------------#
        #   b[0]-b[3]为人脸框的坐标，b[4]为得分
        # ---------------------------------------------------#
        cv2.rectangle(old_image, (b[0], b[1]), (b[2], b[3]), col, 2)
        cx = b[0]
        cy = b[1] + 12
        cv2.putText(old_image, text, (cx, cy),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, col)
        cv2.putText(old_image, emo[i], (cx, cy + 12),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, col)
        i = i + 1

        # print(b[0], b[1], b[2], b[3], b[4])
        # ---------------------------------------------------#
        #   b[5]-b[14]为人脸关键点的坐标
        # ---------------------------------------------------#
        if 0:
            cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)
    return old_image
