import torch
from nets.emotion import ResNet18_ARM___RAF
from nets.retinaface import Retinaface
from  arcface.engine import *
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import config as cfg
emoLabel = ['amaze', 'fear', 'disgust', 'happy', 'sad', 'anger', "neutral"]

retinaface = Retinaface()
cudahere = torch.cuda.is_available()
model = ResNet18_ARM___RAF().cuda() if cudahere else ResNet18_ARM___RAF()
checkpoint = torch.load("model_data/epoch16_acc0.9073(raf-basic).pth", map_location='cuda') if cudahere else torch.load(
    "model_data/epoch16_acc0.9073(raf-basic).pth", map_location='cpu')
model.load_state_dict(checkpoint["model_state_dict"], strict=False)

res,activeFileInfo = ASFGetActiveFileInfo()
if (res != MOK):
    print("ASFGetActiveFileInfo fail: {}".format(res))
else:
    print(activeFileInfo)
# face_engine = ArcFace()
mask = ASF_FACE_DETECT | ASF_FACERECOGNITION | ASF_AGE | ASF_GENDER |ASF_FACE3DANGLE | ASF_LIVENESS | ASF_IR_LIVENESS
# res = face_engine.ASFInitEngine(ASF_DETECT_MODE_VIDEO,ASF_OP_0_ONLY,16,10,mask)
# if (res != MOK):
#     print("ASFInitEngine fail: {}".format(res) )
# else:
#     print("ASFInitEngine sucess: {}".format(res))

face_img_engine = ArcFace()  #engine中一个类
res = face_img_engine.ASFInitEngine(ASF_DETECT_MODE_IMAGE,ASF_OP_0_ONLY,30,10,mask)
if (res != 0):
    print("ASFInitEngine(img) fail")
else:
    print("ASFInitEngine(img) sucess")
secret_id = cfg.cos_cfg["secret_id"] 
secret_key = cfg.cos_cfg["secret_key"] 
region = cfg.cos_cfg["region"]
                           
token = None               
scheme = 'https'         

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)

bucket = cfg.cos_cfg["bucket"]