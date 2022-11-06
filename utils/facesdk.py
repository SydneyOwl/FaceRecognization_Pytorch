import cv2
import numpy as np
from arcface.struct_info import ASF_MultiFaceInfo, ASF_SingleFaceInfo
from utils import MOK, ASF_AGE, ASF_GENDER, ASF_FACE_DETECT, ASF_FACERECOGNITION,face_img_engine
from uuid import uuid4
from utils.picupload import upload_byte_to_cos

def deprecated(funct):
    def func(funct):
        return None
    return func

def calcNewFaceInFrame(boxes_conf_landms,source,recoginzed_face):
    i = 0
    face_detail = {}
    for b in boxes_conf_landms:
        b = list(map(int, b))
        # print(type(b[1]))
        # top = b[1]
        # bot = b[3]
        # lef = b[0]
        # rig = b[2]
        # top = max(0,np.floor(top + 0.5).astype('int32'))
        # lef = max(0,np.floor(lef + 0.5).astype('int32'))
        # bot = min(source.size[1],np.floor(bot + 0.5).astype('int32'))
        # rig = min(source.size[0],np.floor(rig + 0.5).astype('int32'))
        # pic =source[top:bot,lef:rig]
        x1 = np.maximum(b[0],0)
        x2 = np.minimum(b[2],source.shape[1])
        y1 = np.maximum(b[1],0)
        y2 = np.minimum(b[3],source.shape[0])
        pic = source[y1:y2,x1:x2]
        sp = pic.shape
        try:
            source1 = cv2.resize(pic, (sp[1]*4,sp[0]*4)) 
        except cv2.error as e:
            print(e)
            continue
        face_detail[i]=source1
        i+=1
    ans = getNewFace(recoginzed_face,face_detail)
    return ans

def getFaceSimilarity(s1, s2):
    return face_img_engine.ASFFaceFeatureCompare(s1, s2)


def getFacePos(img):
    res, detectedFaces1 = face_img_engine.ASFDetectFaces(img)
    return detectedFaces1.faceRect[0]

def getNewFace(recoginzed_face:list,face_dict:dict):
    processMask = ASF_AGE | ASF_GENDER 
    result = {}
    # 检测第一张图中的人脸
    for k,img in face_dict.items():
        inCycle = {}
        res, detectedFaces1 = face_img_engine.ASFDetectFaces(img)
        if detectedFaces1.faceNum==0:continue
        threshold = 0.7  # 阈值
        if res == MOK:
            single_detected_face1 = ASF_SingleFaceInfo()
            single_detected_face1.faceRect = detectedFaces1.faceRect[0]
            single_detected_face1.faceOrient = detectedFaces1.faceOrient[0]
            res, fea = face_img_engine.ASFFaceFeatureExtract(img, single_detected_face1)
            if (res != MOK):
                print("ASFFaceFeatureExtract error"+str(res))
                continue
            flag = 0
            for feature in recoginzed_face:
                tg = getFaceSimilarity(
                    fea, feature)[1]
                if tg >= threshold:
                    flag = 1
                    break
            if flag:continue
            recoginzed_face.append(fea)
            res = face_img_engine.ASFProcess(img, detectedFaces1, processMask)
            if res == MOK:
                res, ageInfo = face_img_engine.ASFGetAge()
                if (res != MOK):
                    print("ASFGetAge fail: {}".format(res))
                    continue
                else:
                    inCycle["age"]=ageInfo.ageArray[0]
                res, genderInfo = face_img_engine.ASFGetGender()
                if (res != MOK):
                    print("ASFGetGender fail: {}".format(res))
                    continue
                else:
                    inCycle["gender"]=genderInfo.genderArray[0]
            else:
                print("cannot get age and gender"+str(res))
                continue
            tg,img = cv2.imencode('.jpg', img)
            if tg:
                url = upload_byte_to_cos(img.tobytes(),str(uuid4()))
                inCycle["faceThumb"]=url
            result[k]=inCycle
        else:
            print("ASFDetectFaces returned a non-zero")
            continue
    return result


@deprecated
def discoverNewFace(frame: any, recoginzedFace: list, faceDetail: dict, pos: dict,debug=False):
    processMask = ASF_AGE | ASF_GENDER 
    flag = 0
    max_box = 200  # 判定人脸位置相同的阈值
    threshold = 0.7  # 阈值
    res, detectedFaces = face_engine.ASFDetectFaces(frame)
    new = {}
    age = 0
    gender = 0
    if res == 0:
        faceNum = detectedFaces.faceNum
        print("facenum"+str(faceNum))
        for face in range(faceNum):
            ra = detectedFaces.faceRect[face]  # 如果不超过指定值，认为retinaface识别的脸和这个相同
            for k, v in pos.items():  # LTRB
                if debug or (v[0]-ra.left < max_box and v[1]-ra.top < max_box \
                        and v[2]-ra.right < max_box and v[3]-ra.bottom < max_box):
                    faceID = detectedFaces.faceID[face]
                    if faceID not in recoginzedFace:
                        # age, gender, feature = getFaceFeature(smallFaceList[k])
                        single_detected_face1 = ASF_SingleFaceInfo()
                        single_detected_face1.faceRect = detectedFaces.faceRect[face]
                        single_detected_face1.faceOrient = detectedFaces.faceOrient[face]
                        res, single_feature = face_engine.ASFFaceFeatureExtract(
                            frame, single_detected_face1)
                        for i in recoginzedFace:
                            tg = getFaceSimilarity(
                                single_feature, faceDetail[i]["feature"])[1]
                            if tg >= threshold:
                                flag = 1
                                recoginzedFace.append(faceID)
                                break
                        if flag == 0:
                            # face_owl = ASF_MultiFaceInfo()
                            # face_owl.faceNum = 1
                            # face_owl.faceRect = detectedFaces.faceRect
                            # face_owl.faceOrient = detectedFaces.faceOrient
                            #不考虑超过四张脸。。。。会有bug
                            res = face_img_engine.ASFProcess(
                                frame, detectedFaces, processMask)
                            if res == MOK:
                                res, ageInfo = face_img_engine.ASFGetAge()
                                if (res != MOK):
                                    print("ASFGetAge fail: {}".format(res))
                                else:
                                    age = ageInfo.ageArray[0]
                                res, genderInfo = face_img_engine.ASFGetGender()
                                if (res != MOK):
                                    print("ASFGetGender fail: {}".format(res))
                                else:
                                    gender = genderInfo.genderArray[0]
                            else:
                                print("failed:"+str(res))
                            faceDetail[faceID] = {
                                "age": age,
                                "gender": gender,
                                "feature": single_feature
                            }
                            new[k] = {"age": age,
                                      "gender": gender}  # 新出现的
                            recoginzedFace.append(faceID)
    else:
        print("ASFDetectFaces error:"+str(res))
    return new
