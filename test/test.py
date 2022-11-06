
# -*- coding=utf-8
def owl():
    import numpy as np
    import torch
    from utils.videoutil import cutToFit
    from nets.emotion import ResNet18_ARM___RAF
    import cv2
    from nets.retinaface import Retinaface
    from utils import facesdk,face_img_engine
    from PIL import Image
    MONITOR_STREAM = ""#YOUR_IP

    cudahere = torch.cuda.is_available()
    retinaface = Retinaface()
    model = ResNet18_ARM___RAF().cuda() if cudahere else ResNet18_ARM___RAF()
    checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cuda') if cudahere else torch.load("model_data/epoch16_acc0.9073(raf-basic).pth",map_location='cpu')
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    source = cv2.imread("./test.jpg")
    recoginzed_face = []
    face_detail = {}
    # frame = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
    _, face_list, _, boxes_conf_landms = retinaface.detect_image_return_flist(source)
    if face_list != []:
        # print(type(boxes_conf_landms))
        i = 0
        for b in boxes_conf_landms:
            b = list(map(int, b))
            # print(type(b[1]))
            top = b[1]
            bot = b[3]
            lef = b[0]
            rig = b[2]
            top = int(np.floor(top + 0.5).astype('int32'))
            lef = int(np.floor(lef + 0.5).astype('int32'))
            bot = int(np.floor(bot - 0.5).astype('int32'))
            rig = int(np.floor(rig - 0.5).astype('int32'))
            pic =source[top:bot,lef:rig]
            sp = pic.shape
            print(sp)
            try:
                source1 = cv2.resize(pic, (sp[1]*4,sp[0]*4)) 
            except cv2.error:
                continue
            # print(face_img_engine.ASFDetectFaces(source))
            # img = cv2.resize(pic, (sp[1]//4*4, sp[0]//4*4))
            # cv2.imwrite("./"+str(i)+".jpg",img)
            # face_detail[i] = cv2.resize(source[top:but,lef:rig], ((but-top)//4*4, (rig-lef)//4*4))
            face_detail[i]=source1
            i+=1
        ans = facesdk.getNewFace(recoginzed_face,face_detail)
        print(ans)
    # ans = cv2.imread("test"+".jpg")
    # sp = ans.shape
    # img = cv2.resize(ans, (sp[1]//4*4, sp[0]//4*4))
    # ans = facesdk.getNewFace(recoginzed_face,face_detail)
def owl1():
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
    import config


    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    secret_id = config.cos_cfg["secret_id"]     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
    secret_key = config.cos_cfg["secret_key"]   # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
    region = config.cos_cfg["region"]      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                            # COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
    token = None               # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
    scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)

    #### 文件流简单上传（不支持超过5G的文件，推荐使用下方高级上传接口）
    # 强烈建议您以二进制模式(binary mode)打开文件,否则可能会导致错误
    with open('test.jpg', 'rb') as fp:
        response = client.put_object(
            Bucket='face-1304122906',
            Body=fp,
            Key='test.jpg',
            StorageClass='STANDARD',
            EnableMD5=False
        )
    print(response['ETag'])
from utils import client,bucket,region
from uuid import uuid4
def upload_to_bed(path):
    picName = str(uuid4())
    with open(path, 'rb') as fp:
        client.put_object(
            Bucket=bucket,
            Body=fp,
            Key='/thumb/{}.jpg'.format(picName),
            StorageClass='STANDARD',
            EnableMD5=False
        )
    return "https://{}.cos.{}.myqcloud.com/thumb/{}.jpg".format(bucket,region,picName)
print(upload_to_bed("/home/ubuntu/Fer/lss/FR/test.jpg"))